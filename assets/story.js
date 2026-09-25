// Cuddleya Startseite. Eigener Code ohne Fremdbibliothek; speichert nichts und sendet nichts.
// Himmel nach dem Scrollstand, Stationen beim Hereinscrollen, Figuren zum Antippen.
(() => {
  const doc = document.documentElement;
  doc.classList.add("js");
  const still = matchMedia("(prefers-reduced-motion: reduce)");
  const clamp = (x) => Math.min(1, Math.max(0, x));
  const bump = (p) => (p > 0 && p < 1 ? Math.sin(Math.PI * p) : 0);

  // Figuren: Antippen lässt sie einschlafen oder aufwachen (gedrückt = schläft).
  for (const b of document.querySelectorAll(".fig-btn")) {
    b.addEventListener("click", () => {
      b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true"));
    });
  }

  // Zähler auf den Beispielbildern laufen, sobald ihre Station zu sehen ist.
  const pad = (n) => String(n).padStart(2, "0");
  const clock = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor(s / 60) % 60;
    return (h ? h + ":" + pad(m) : m) + ":" + pad(s % 60);
  };
  // Aus der Uhrzeit gerechnet, damit ein pausierter Tab nicht nachhinkt; im Hintergrund wird nicht geschrieben.
  const tick = (root) => {
    for (const el of root.querySelectorAll("[data-timer]")) {
      const start = Date.now() - Number(el.dataset.timer) * 1000;
      setInterval(() => {
        if (!document.hidden) el.textContent = clock(Math.floor((Date.now() - start) / 1000));
      }, 1000);
    }
  };

  const sky = document.querySelector(".sky");
  const dawn = document.querySelector('[data-sky="dawn"]');
  const dusk = document.querySelector('[data-sky="dusk"]');
  const stations = document.querySelectorAll(".st");

  // 0, solange die Szene unter dem oberen Rand liegt, 1, wenn ihr klebender Teil losgelassen wird.
  // Gemessen am klebenden Teil (fest in svh), nicht an der Fensterhöhe: die springt mit der iOS-Leiste.
  const progress = (el) => {
    const r = el.getBoundingClientRect();
    return clamp(-r.top / Math.max(1, r.height - el.firstElementChild.offsetHeight));
  };
  const written = new Map();
  const setIfChanged = (el, name, value) => {
    const key = name + (el === sky ? "s" : el.id);
    if (written.get(key) === value) return;
    written.set(key, value);
    el.style.setProperty(name, value);
  };

  // Geht etwas schief, zeigt die Seite ihre Standbilder, statt Inhalte unsichtbar zu lassen.
  let on = false;
  const giveUp = (err) => {
    on = false;
    doc.classList.remove("motion");
    removeEventListener("scroll", request);
    removeEventListener("resize", request);
    for (const s of stations) s.classList.add("is-in");
    console.error("story.js", err);
  };

  let queued = false;
  const paint = () => {
    queued = false;
    try {
      draw();
    } catch (err) {
      giveUp(err);
    }
  };
  const draw = () => {
    const a = progress(dawn);
    const d = progress(dusk);
    setIfChanged(dawn, "--p", a.toFixed(3));
    setIfChanged(dusk, "--p", d.toFixed(3));
    const night = d > 0 ? clamp((d - 0.35) / 0.5) : 1 - clamp((a - 0.15) / 0.5);
    setIfChanged(sky, "--night-o", night.toFixed(3));
    setIfChanged(sky, "--glow", Math.max(bump(a), bump(d)).toFixed(3));
  };
  const request = () => {
    if (!queued) {
      queued = true;
      requestAnimationFrame(paint);
    }
  };

  const seen = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      e.target.classList.add("is-in");
      seen.unobserve(e.target);
      tick(e.target);
    }
  }, { threshold: 0, rootMargin: "0px 0px -15% 0px" }) : null;

  const setMotion = () => {
    const want = !still.matches && Boolean(sky && dawn && dusk && seen);
    doc.classList.toggle("motion", want);
    if (want && !on) {
      addEventListener("scroll", request, { passive: true });
      addEventListener("resize", request);
      for (const s of stations) if (!s.classList.contains("is-in")) seen.observe(s);
    } else if (!want && on) {
      removeEventListener("scroll", request);
      removeEventListener("resize", request);
      seen?.disconnect();
      for (const s of stations) s.classList.add("is-in");
    }
    on = want;
    if (want) paint();
  };
  try {
    if (still.addEventListener) still.addEventListener?.("change", setMotion);
    else still.addListener?.(setMotion);
    setMotion();
    doc.dataset.story = "1";
  } catch (err) {
    giveUp(err);
  }
})();
