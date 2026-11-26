/**
 * Gumroad Ping -> GA4 "purchase" (real money only)
 * =================================================
 * Why this exists: the browser can only see a CLICK on the buy button. It can
 * never see whether payment completed (Gumroad hosts checkout). The old
 * `purchase_intent` event faked revenue with value/currency params and was
 * renamed to `checkout_click` with no money params. This endpoint is the ONLY
 * place that emits a real GA4 purchase, and it only fires on a signed ping
 * from Gumroad.
 *
 * Setup:
 *   1. Cloudflare Pages -> Settings -> Environment variables (Production):
 *        GA4_MEASUREMENT_ID = G-XXXXXXXXXX   (same as src/consts.ts)
 *        GA4_API_SECRET    = <Measurement Protocol API secret, from
 *                            GA4 Admin > Data streams > your stream >
 *                            Measurement Protocol > Create secret>
 *        GUMROAD_WEBHOOK_TOKEN = <long random string you generate>
 *        GUMROAD_PING_SECRET   = (optional) the secret set in Gumroad
 *                                Settings > Advanced > Ping > secret
 *   2. Gumroad -> Settings -> Advanced -> Ping URL:
 *        https://powerbitutorials.com/api/gumroad-webhook?token=<same token>
 *   3. Click "Send test ping" — response must be JSON with "accepted": false
 *      and reason "test ping" (test pings NEVER become GA4 revenue).
 *
 * Notes on the wire format (verified against Gumroad docs):
 *   - Body is application/x-www-form-urlencoded, NOT JSON.
 *   - `price` is USD CENTS regardless of the `currency` field.
 *   - `resource_name` = "sale" | "refund" | "dispute" ...
 *   - `test` = true for self-purchases / test pings.
 *   - `url_params` carries custom query params we append to product URLs,
 *     which is how the browser's GA4 client_id comes back to us.
 *   - Delivery is at-least-once; GA4 dedupes on transaction_id, so we do not
 *     need a KV store for correctness.
 */

const GA4_MP_ENDPOINT = "https://www.google-analytics.com/mp/collect";

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

/** Stable, non-PII client id fallback when no client_id came through url_params. */
async function stableClientId(email) {
  const seed = email || "gumroad-anon";
  const bytes = new TextEncoder().encode(seed);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const hex = Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  // GA4 expects a numeric-looking client_id; keep it deterministic per buyer.
  return `${parseInt(hex.slice(0, 12), 16)}.${parseInt(hex.slice(12, 24), 16)}`;
}

function parseUrlParams(raw) {
  // Gumroad sends url_params as a JSON-ish string; tolerate both plain and
  // double-encoded values so a bad encoding never drops a real sale.
  if (!raw) return {};
  for (const attempt of [raw, decodeURIComponent(raw)]) {
    try {
      const value = typeof attempt === "string" ? JSON.parse(attempt) : attempt;
      if (value && typeof value === "object") return value;
    } catch (_) {
      // try next decoding
    }
  }
  return {};
}

async function verifySignature(request, rawBody, secret) {
  if (!secret) return true; // token-in-URL is the primary gate when no secret set
  const header =
    request.headers.get("X-Gumroad-Signature") ||
    request.headers.get("x-gumroad-signature");
  if (!header) return false;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(rawBody));
  const expected = Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  // constant-time-ish compare
  if (header.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < header.length; i++) diff |= header.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

async function sendToGA4(env, clientId, event) {
  const url = new URL(GA4_MP_ENDPOINT);
  url.searchParams.set("measurement_id", env.GA4_MEASUREMENT_ID);
  url.searchParams.set("api_secret", env.GA4_API_SECRET);
  //MP responses body even on success; a 2xx is the only success signal.
  const res = await fetch(url.toString(), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ client_id: clientId, events: [event] }),
  });
  return res.status;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  // Gate 1: shared token in the URL. Without it anyone could post fake revenue.
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (!env.GUMROAD_WEBHOOK_TOKEN || token !== env.GUMROAD_WEBHOOK_TOKEN) {
    return json({ accepted: false, reason: "unauthorized" }, 401);
  }
  if (!env.GA4_MEASUREMENT_ID || !env.GA4_API_SECRET) {
    return json({ accepted: false, reason: "GA4 credentials not configured" }, 503);
  }

  const rawBody = await request.text();
  if (!(await verifySignature(request, rawBody, env.GUMROAD_PING_SECRET))) {
    return json({ accepted: false, reason: "bad signature" }, 401);
  }

  // Gumroad Ping is form-urlencoded.
  let sale;
  try {
    sale = Object.fromEntries(new URLSearchParams(rawBody).entries());
  } catch (_) {
    return json({ accepted: false, reason: "malformed body" }, 400);
  }

  // test pings and self-purchases must never show up as revenue
  if (sale.test === "true" || sale.test === "1") {
    // ACK with 2xx: Gumroad does not retry 4xx, and we do not want a test ping
    // to be redelivered three times.
    return json({ accepted: false, reason: "test ping" });
  }

  const resource = sale.resource_name || "sale";
  const saleId = sale.sale_id;
  if (!saleId) return json({ accepted: false, reason: "missing sale_id" }, 400);

  const cents = Number(sale.price || 0);
  const value = Number.isFinite(cents) ? cents / 100 : 0;
  const currency = sale.currency || "USD";
  const product = sale.product_name || "unknown";
  const productId = sale.short_product_id || sale.product_id || "unknown";
  const params = parseUrlParams(sale.url_params);
  const clientId = params.client_id || (await stableClientId(sale.email));

  let event;
  if (resource === "refund") {
    event = {
      name: "refund",
      params: {
        transaction_id: saleId,
        value,
        currency,
      },
    };
  } else if (resource === "sale") {
    event = {
      name: "purchase",
      params: {
        transaction_id: saleId,
        value,
        currency,
        items: [
          {
            item_id: productId,
            item_name: product,
            price: value,
            quantity: Number(sale.quantity || 1),
          },
        ],
        // Attribution breadcrumbs only (never email — that is PII).
        source_page: params.source_url || null,
        campaign: params.campaignid || null,
      },
    };
    // drop null-valued params; GA4 rejects some custom params with null
    Object.keys(event.params).forEach((k) => {
      if (event.params[k] === null) delete event.params[k];
    });
  } else {
    // dispute / dispute_won / other resource types: acknowledge but do not
    // create revenue events. Refunds are the only other money event we track.
    return json({ accepted: false, reason: `ignored resource: ${resource}` });
  }

  try {
    const status = await sendToGA4(env, clientId, event);
    if (status >= 300) {
      // 5xx from GA4 is retryable; return 502 so Gumroad redelivers.
      return json({ accepted: false, reason: "ga4 error", status }, 502);
    }
    return json({
      accepted: true,
      resource,
      product,
      value,
      currency,
      transaction_id: saleId,
      attributed_client: params.client_id ? "browser" : "buyer-hash",
    });
  } catch (e) {
    return json({ accepted: false, reason: "forward failed", error: String(e) }, 502);
  }
}

export async function onRequestGet() {
  return json({ ok: true, hint: "POST Gumroad Ping here with ?token=..." });
}
