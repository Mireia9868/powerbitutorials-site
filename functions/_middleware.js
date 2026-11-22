// Redirect the www host to the apex domain with a 301.
// Bing / Google treat www and apex as two hosts; the sitemap only lists the
// apex, so every www URL otherwise shows up as "missing from sitemap".
export const onRequest = ({ request, next }) => {
  const url = new URL(request.url);
  if (url.hostname.startsWith("www.")) {
    url.hostname = url.hostname.slice(4);
    return Response.redirect(url.toString(), 301);
  }
  return next();
};
