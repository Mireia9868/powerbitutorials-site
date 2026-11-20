    (function () {
      var COLORS = ["#C0392B", "#E0A80C", "#1E7B4F", "#1F3A5F"];

      var els = {
        measure: document.getElementById("measure"),
        name: document.getElementById("name"),
        mode: document.getElementById("mode"),
        direction: document.getElementById("direction"),
        asVar: document.getElementById("as-var"),
        withBlank: document.getElementById("with-blank"),
        bands: document.getElementById("bands"),
        output: document.getElementById("output"),
        copy: document.getElementById("copy-btn"),
      };
      if (!els.output) return;

      function bandFields(n) {
        var defaults = [0, 0.15, 0.3];
        var html = "";
        for (var i = 0; i < n; i++) {
          html +=
            '<div class="band-row">' +
            "<label>Threshold " + (i + 1) + "</label>" +
            '<input type="number" step="any" class="thr" value="' + defaults[i] + '">' +
            '<input type="color" class="clr" value="' + COLORS[i] + '">' +
            "</div>";
        }
        html +=
          '<div class="band-row final">' +
          "<label>Everything else</label>" +
          '<span class="final-swatch" style="background:' + COLORS[n] + '"></span>' +
          '<span class="final-label">' + COLORS[n] + "</span>" +
          "</div>";
        els.bands.innerHTML = html;
      }

      function indent(lines, spaces) {
        var pad = new Array(spaces + 1).join(" ");
        return lines.map(function (l) { return l === "" ? "" : pad + l; });
      }

      function build() {
        var measure = (els.measure.value || "").trim() || "[Value]";
        var name = (els.name.value || "").trim() || "Colour";
        var lowBad = els.direction.value !== "high";
        var useVar = els.asVar.checked;
        var guardBlank = els.withBlank.checked;

        var thrs = Array.prototype.map.call(els.bands.querySelectorAll(".thr"), function (el) {
          return parseFloat(el.value);
        });
        var clrs = Array.prototype.map.call(els.bands.querySelectorAll(".clr"), function (el) {
          return el.value.toUpperCase();
        });
        var finalColor = COLORS[clrs.length];
        var lastEl = els.bands.querySelector(".final .final-label");
        if (lastEl) finalColor = lastEl.textContent.trim();

        // 高值有害时，只需要把阈值反过来；颜色顺序不变
        if (!lowBad) thrs.reverse();

        var value = useVar ? "_v" : measure;
        var op = lowBad ? " < " : " > ";

        var sw = ["SWITCH (", "    TRUE (),"];
        thrs.forEach(function (t, i) {
          sw.push("    " + value + op + t + ', "' + clrs[i] + '",');
        });
        sw.push('    "' + finalColor + '"');
        sw.push(")");

        var body = sw;
        if (guardBlank) {
          var inner = indent(sw, 8);
          body = ["IF (", "    ISBLANK ( " + value + " ),", "    BLANK (),"].concat(inner, [")"]);
        }

        var lines = [name + " ="];
        if (useVar) {
          lines.push("VAR _v = " + measure);
          lines.push("RETURN");
          body = indent(body, 4);
        }
        lines = lines.concat(body);

        els.output.textContent = lines.join("\n");
      }

      function copy() {
        var text = els.output.textContent;
        function done() {
          els.copy.textContent = "Copied";
          setTimeout(function () { els.copy.textContent = "Copy"; }, 1400);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, fallback);
        } else fallback();
        function fallback() {
          var ta = document.createElement("textarea");
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand("copy"); done(); } catch (e) {}
          document.body.removeChild(ta);
        }
      }

      els.mode.addEventListener("change", function () {
        bandFields(parseInt(els.mode.value, 10) - 1);
        build();
      });
      document.addEventListener("input", function (e) {
        if (e.target && (e.target.classList.contains("thr") || e.target.classList.contains("clr"))) build();
      });
      ["measure", "name", "direction", "as-var", "with-blank"].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) {
          el.addEventListener("input", build);
          el.addEventListener("change", build);
        }
      });
      els.copy.addEventListener("click", copy);

      document.getElementById("preset-pl").addEventListener("click", function () {
        els.mode.value = "2";
        bandFields(1);
        els.direction.value = "low";
        els.bands.querySelectorAll(".thr")[0].value = "0";
        els.bands.querySelectorAll(".clr")[0].value = "#C0392B";
        build();
      });
      document.getElementById("preset-tl").addEventListener("click", function () {
        els.mode.value = "3";
        bandFields(2);
        els.direction.value = "low";
        var thrs = els.bands.querySelectorAll(".thr");
        var clrs = els.bands.querySelectorAll(".clr");
        thrs[0].value = "0";
        thrs[1].value = "0.15";
        clrs[0].value = "#C0392B";
        clrs[1].value = "#E0A80C";
        build();
      });

      bandFields(2);
      build();
    })();
