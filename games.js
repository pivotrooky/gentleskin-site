// The two little toys on the home page: the urge wave and the kelp pods.
// Colors from the app's shared/tokens.toml.
(function () {
  var C = {
    waterFar: "#C5D6CE", waterMid: "#A3BFB2", waterNear: "#88AA9B", foam: "#F0F7F2",
    star: "#DE8E7C", starStroke: "#C06B54", starLight: "#E8AA9A", face: "#4A2E22", blush: "#C4643F",
    rose: "#8E4B55", ink: "#3E2B29", sub: "#A17E8B",
  };
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  function track(name, props) { if (window.posthog) posthog.capture(name, props || {}); }

  // ---------- The wave ----------
  var canvas = document.getElementById("wave");
  if (canvas) {
    var ctx = canvas.getContext("2d");
    var label = document.getElementById("wave-label");
    var HOLD = 10;            // seconds of holding until the urge passes (the app uses 30)
    var held = 0, holding = false, done = false, started = false;
    var t0 = performance.now(), last = t0, W = 0, H = 0, dpr = 1;

    function size() {
      dpr = window.devicePixelRatio || 1;
      W = canvas.clientWidth; H = canvas.clientHeight;
      canvas.width = W * dpr; canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    size(); window.addEventListener("resize", size);

    // Height of a water band at x: a few sines, calmer as the urge passes.
    function surface(x, t, base, amp, speed, phase) {
      return base + amp * (Math.sin(x / 70 + t * speed + phase) * 0.6 +
                           Math.sin(x / 31 - t * speed * 1.3 + phase * 2) * 0.25 +
                           Math.sin(x / 140 + t * speed * 0.5) * 0.4);
    }
    function band(t, base, amp, speed, phase, color) {
      ctx.beginPath(); ctx.moveTo(0, H);
      for (var x = 0; x <= W + 8; x += 8) ctx.lineTo(x, surface(x, t, base, amp, speed, phase));
      ctx.lineTo(W, H); ctx.closePath(); ctx.fillStyle = color; ctx.fill();
    }
    function star(x, y, r, rot, calm) {
      ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
      ctx.beginPath();
      for (var i = 0; i < 10; i++) {
        var a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.56 : r;
        ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
      }
      ctx.closePath();
      ctx.lineJoin = "round";
      ctx.lineWidth = r * 0.42; ctx.strokeStyle = C.starStroke; ctx.stroke();
      ctx.lineWidth = r * 0.32; ctx.strokeStyle = C.star; ctx.stroke();
      ctx.fillStyle = C.star; ctx.fill();
      // a soft highlight
      ctx.beginPath(); ctx.ellipse(-r * 0.22, -r * 0.3, r * 0.22, r * 0.12, -0.5, 0, Math.PI * 2);
      ctx.fillStyle = C.starLight; ctx.globalAlpha = 0.7; ctx.fill(); ctx.globalAlpha = 1;
      // blush
      ctx.fillStyle = C.blush; ctx.globalAlpha = 0.28;
      ctx.beginPath(); ctx.arc(-r * 0.34, r * 0.12, r * 0.11, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(r * 0.34, r * 0.12, r * 0.11, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 1;
      // closed happy eyes and a smile that widens as it calms
      ctx.strokeStyle = C.face; ctx.lineWidth = Math.max(1.6, r * 0.07); ctx.lineCap = "round";
      ctx.beginPath(); ctx.arc(-r * 0.2, -r * 0.02, r * 0.09, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();
      ctx.beginPath(); ctx.arc(r * 0.2, -r * 0.02, r * 0.09, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, r * 0.08, r * (0.12 + 0.06 * calm), Math.PI * 0.15, Math.PI * 0.85); ctx.stroke();
      ctx.restore();
    }
    function ring(p) {
      var x = W - 34, y = 34, r = 18;
      ctx.lineWidth = 4; ctx.lineCap = "round";
      ctx.strokeStyle = "rgba(142,75,85,.15)"; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
      ctx.strokeStyle = C.rose; ctx.beginPath(); ctx.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + p * Math.PI * 2); ctx.stroke();
    }

    function frame(now) {
      var dt = Math.min(0.05, (now - last) / 1000); last = now;
      if (holding && !done) {
        held += dt;
        if (held >= HOLD) { done = true; holding = false; label.textContent = "It passed. Tap to ride another."; track("web_wave_done"); }
      }
      var p = Math.min(1, held / HOLD);
      var t = (now - t0) / 1000 * (reduced ? 0.3 : 1);
      var amp = 16 * (1 - 0.75 * p) + 3;
      ctx.clearRect(0, 0, W, H);
      var base = H * 0.55;
      band(t, base - 22, amp * 0.8, 0.6, 1.3, C.waterFar);
      band(t, base - 8, amp * 0.9, 0.8, 2.1, C.waterMid);
      var r = Math.min(44, W / 9);
      var sx = W * 0.5, sy = surface(sx, t, base + 6, amp, 1.0, 0.4) - r * 0.55;
      var tilt = (surface(sx + 10, t, base + 6, amp, 1.0, 0.4) - surface(sx - 10, t, base + 6, amp, 1.0, 0.4)) / 30;
      star(sx, sy, r, tilt, p);
      band(t, base + 6, amp, 1.0, 0.4, C.waterNear);
      if (started) ring(p);
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    function down(e) {
      e.preventDefault();
      if (done) { done = false; held = 0; }
      if (!started) { started = true; track("web_wave_start"); }
      holding = true; label.textContent = "Keep your finger on the water…";
    }
    function up() {
      if (holding && !done) label.textContent = "Hold again when you're ready.";
      holding = false;
    }
    canvas.addEventListener("pointerdown", down);
    window.addEventListener("pointerup", up);
    canvas.addEventListener("pointerleave", up);
    canvas.addEventListener("keydown", function (e) { if (e.key === " " || e.key === "Enter") down(e); });
    canvas.addEventListener("keyup", up);
  }

  // ---------- The kelp pods ----------
  var field = document.getElementById("pods");
  if (field) {
    var count = document.getElementById("pods-count");
    var N = 24, popped = 0, first = true;
    function build() {
      field.innerHTML = ""; popped = 0; count.textContent = "0 of " + N;
      for (var i = 0; i < N; i++) {
        var b = document.createElement("button");
        b.className = "pod"; b.type = "button"; b.setAttribute("aria-label", "Pop");
        b.style.setProperty("--s", (0.75 + Math.random() * 0.35).toFixed(2));
        b.style.setProperty("--d", (Math.random() * 3).toFixed(2) + "s");
        b.addEventListener("click", pop);
        field.appendChild(b);
      }
    }
    function pop(e) {
      var b = e.currentTarget;
      if (b.classList.contains("popped")) return;
      if (first) { first = false; track("web_pop_start"); }
      b.classList.add("popped"); b.disabled = true;
      popped++; count.textContent = popped + " of " + N;
      if (navigator.vibrate) navigator.vibrate(8);
      if (popped === N) {
        count.textContent = "All popped.";
        track("web_pop_done");
        setTimeout(build, 1600);
      }
    }
    build();
  }
})();
