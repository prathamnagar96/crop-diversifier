/* KrishiKavach — farmer app (vanilla JS, no build step). */
(() => {
  "use strict";

  // ---------------------------------------------------------------- storage
  const store = {
    get(k, d) { try { const v = localStorage.getItem("kk_" + k); return v ? JSON.parse(v) : d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem("kk_" + k, JSON.stringify(v)); } catch { /* private mode */ } },
  };

  const month = new Date().getMonth() + 1;
  const defaultSeason = month >= 10 || month <= 2 ? "rabi" : "kharif";

  const S = {
    lang: store.get("lang", "mr"),
    profile: store.get("profile", { district: null, soil: null, water: null, season: defaultSeason }),
    results: store.get("results", null),
    meta: null,
    summary: null,
    chat: [],
    fb: { crop: null, quintals: 5, rating: null },
    lastRoute: "home",
  };

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const view = $("#view");
  const phone = $("#phone");
  const LOCALE = { mr: "mr-IN", hi: "hi-IN", en: "en-IN" };

  // ---------------------------------------------------------------- i18n
  function t(key, vars = {}) {
    const dict = window.I18N[S.lang] || window.I18N.en;
    let s = dict[key] ?? window.I18N.en[key] ?? key;
    if (typeof s === "string") s = s.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
    return s;
  }
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => new Intl.NumberFormat(LOCALE[S.lang]).format(n);
  const cropName = (id) => S.meta?.crops[id]?.name[S.lang] || id;
  const distName = (id) => S.meta?.districts[id]?.[S.lang] || id;

  function applyStatic() {
    document.documentElement.lang = S.lang;
    $$("[data-t]").forEach((el) => { el.textContent = t(el.dataset.t); });
    $$(".lang button").forEach((b) => b.classList.toggle("on", b.dataset.lang === S.lang));
    $("#chatText").placeholder = t("chat_ph");
    renderChips();
    setChatMode();
  }

  // ---------------------------------------------------------------- photos
  function photo(key, extra = "") {
    const im = window.IMAGES[key] || window.IMAGES.hero;
    return `<div class="ph ${extra}" style="--tint:${im.tint}"><div class="ph-fallback">${im.emoji}</div><img alt="" data-key="${key}"></div>`;
  }
  function hydrate(root = document) {
    $$("img[data-key]:not([src])", root).forEach((img) => {
      const key = img.dataset.key;
      const im = window.IMAGES[key];
      const local = S.meta?.local_images?.includes(key);
      img.onload = () => { img.classList.add("ok"); img.parentElement.classList.add("loaded"); };
      img.onerror = () => {
        if (img.dataset.tried !== "remote" && local) { img.dataset.tried = "remote"; img.src = im.url; return; }
        img.remove();
      };
      img.referrerPolicy = "no-referrer";
      img.src = local ? `img/${key}.jpg` : im.url;
    });
  }

  // ---------------------------------------------------------------- speech
  let speakingBtn = null;
  function speak(text, btn) {
    if (!("speechSynthesis" in window)) return;
    const synth = window.speechSynthesis;
    if (synth.speaking && speakingBtn === btn) { synth.cancel(); btn?.classList.remove("talking"); speakingBtn = null; return; }
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text.replace(/[•✓]/g, ""));
    const voices = synth.getVoices();
    const want = LOCALE[S.lang];
    const v = voices.find((x) => x.lang === want) || voices.find((x) => x.lang.startsWith(S.lang))
      || (S.lang === "mr" && voices.find((x) => x.lang.startsWith("hi")));
    u.lang = v ? v.lang : want;
    if (v) u.voice = v;
    u.rate = 0.92;
    speakingBtn?.classList.remove("talking");
    speakingBtn = btn; btn?.classList.add("talking");
    u.onend = u.onerror = () => { btn?.classList.remove("talking"); if (speakingBtn === btn) speakingBtn = null; };
    synth.speak(u);
  }
  const speakBtn = (text, cls = "") => `<button class="speak ${cls}" data-say="${esc(text)}" aria-label="${esc(t("listen"))}">🔊</button>`;
  view.addEventListener("click", (e) => {
    const b = e.target.closest("[data-say]");
    if (b) { e.preventDefault(); e.stopPropagation(); speak(b.dataset.say, b); }
  });

  // ---------------------------------------------------------------- api
  async function api(path, body) {
    const res = await fetch("/api/" + path, body
      ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
      : undefined);
    if (!res.ok) throw new Error(path + " " + res.status);
    return res.json();
  }

  // ---------------------------------------------------------------- render
  let prevDepth = 0;
  const DEPTH = { home: 0, farm: 1, loading: 2, results: 3, guide: 4, harvest: 1, thanks: 2 };
  function render(name, html) {
    const d = DEPTH[name] ?? 0;
    const back = d < prevDepth;
    prevDepth = d;
    window.speechSynthesis?.cancel();
    view.innerHTML = `<section class="screen ${back ? "back" : ""}" data-screen="${name}">${html}</section>`;
    window.scrollTo({ top: 0 });
    hydrate(view);
    $$(".tabbar a, .navlinks a").forEach((a) => a.classList.toggle("on",
      a.dataset.tab === name || (name === "guide" && a.dataset.tab === "results") || (name === "thanks" && a.dataset.tab === "harvest")
      || (["farm", "loading"].includes(name) && a.dataset.tab === "results")));
  }

  // ---------------------------------------------------------------- home
  function screenHome() {
    const o = S.meta.outlook;
    const pct = Math.round((1 + o.rain_change) * 100);
    const n = S.summary?.all_total ?? 0;
    const sayText = `${t("greeting")} ${t("outlook_" + o.status)}. ${t("outlook_sub")} ${t("cta")}`;
    render("home", `
      <div class="hero">
        ${photo("hero")}
        ${speakBtn(sayText)}
        <div class="hero-text">
          <h1>${esc(t("greeting"))}</h1>
          <p>${esc(t("tagline"))}</p>
        </div>
      </div>

      <div class="home-grid">
      <div class="weather">
        ${photo("dry")}
        <div>
          <span class="chip warn">☀️ El Niño</span>
          <h3>${esc(t("outlook_" + o.status))}</h3>
          <p>${esc(t("outlook_sub"))}</p>
        </div>
        <div class="rainbars">
          <div class="rainbar"><span>🌧️ ${esc(t("normal_year"))}</span><div class="track"><div class="fill" data-w="100"></div></div></div>
          <div class="rainbar"><span>🌦️ ${esc(t("this_year"))}</span><div class="track"><div class="fill low" data-w="${pct}"></div></div></div>
        </div>
      </div>

      <div class="home-actions">
      <button class="cta" data-go="#farm/1">
        <span class="cta-ico">🌱</span>
        <span><b>${esc(t("cta"))}</b><small>${esc(t("cta_sub"))}</small></span>
        <span class="arrow">➜</span>
      </button>

      <div class="tiles2">
        <button class="mini" data-go="#harvest">${photo("farmer")}<div class="t"><b>${esc(t("harvest_card"))}</b><span>${esc(t("harvest_card_sub"))}</span></div></button>
        <button class="mini" data-go="#chat">${photo("clouds")}<div class="t"><b>💬 ${esc(t("chat_card"))}</b><span>${esc(t("chat_card_sub"))}</span></div></button>
      </div>
      </div>
      </div>

      ${n > 0 ? `<div class="community"><div class="faces"><span>😊</span><span>🧑‍🌾</span><span>👩‍🌾</span></div>${esc(t("community", { n: num(n) }))}</div>` : ""}
      <a class="credits-link" href="#" data-credits>${esc(t("credits"))}</a>
    `);
    requestAnimationFrame(() => setTimeout(() => $$(".fill", view).forEach((f) => { f.style.width = f.dataset.w + "%"; }), 150));
  }

  // ---------------------------------------------------------------- wizard
  const STEPS = ["district", "soil", "water", "season"];
  const OPTIONS = { soil: ["black", "medium", "light"], water: ["rain", "well", "canal"], season: ["kharif", "rabi"] };

  function screenFarm(step) {
    step = Math.min(4, Math.max(1, step || 1));
    const field = STEPS[step - 1];
    const q = t("q_" + field);
    let body = "";
    if (field === "district") {
      body = `<div class="districts">${Object.keys(S.meta.districts).map((id, i) => `
        <button class="dist ${S.profile.district === id ? "sel" : ""}" data-pick="district" data-val="${id}" style="animation-delay:${i * 0.03}s">${esc(distName(id))}</button>`).join("")}</div>`;
    } else {
      body = `<div class="opts">${OPTIONS[field].map((v) => `
        <button class="opt ${S.profile[field] === v ? "sel" : ""}" data-pick="${field}" data-val="${v}">
          ${photo(field + "_" + v)}
          <div><b>${esc(t(field + "_" + v))}</b><span>${esc(t(field + "_" + v + "_sub"))}</span></div>
          <i class="tick">✓</i>
        </button>`).join("")}</div>`;
    }
    render("farm", `<div class="wiz">
      <div class="wiz-top">
        <button class="back-btn" data-go="${step === 1 ? "#home" : "#farm/" + (step - 1)}" aria-label="${esc(t("back"))}">←</button>
        <div class="progress"><i style="width:${(step - 1) * 25}%"></i></div>
        <span class="step-lbl">${esc(t("step", { i: step, n: 4 }))}</span>
      </div>
      <div class="q"><h2>${esc(q)}</h2>${speakBtn(q, "inline")}</div>
      ${body}
    </div>`);
    requestAnimationFrame(() => { const bar = $(".progress i", view); if (bar) bar.style.width = step * 25 + "%"; });
  }

  function pick(field, val, btn) {
    S.profile[field] = val;
    store.set("profile", S.profile);
    $$(`[data-pick="${field}"]`, view).forEach((b) => b.classList.toggle("sel", b === btn));
    const step = STEPS.indexOf(field) + 1;
    setTimeout(() => {
      if (step < 4) location.hash = "#farm/" + (step + 1);
      else runRecommend();
    }, 380);
  }

  // ---------------------------------------------------------------- results
  async function runRecommend() {
    render("loading", `
      <div class="loading"><div>
        <svg class="sprout" viewBox="0 0 150 150" aria-hidden="true">
          <ellipse cx="75" cy="128" rx="46" ry="10" fill="#7a4a24" opacity=".85"/>
          <path class="stem" d="M75 126 C75 110 74 100 75 88" stroke="#2e8b57" stroke-width="6" fill="none" stroke-linecap="round"/>
          <path class="leafL" d="M75 92 C58 90 48 78 50 64 C64 64 74 74 75 92Z" fill="#7cc142"/>
          <path class="leafR" d="M75 92 C92 88 102 74 98 60 C84 62 76 74 75 92Z" fill="#5fae3a"/>
          <circle class="drop" cx="40" cy="30" r="4" fill="#6fb1ff"/>
          <circle class="drop" cx="75" cy="22" r="4" fill="#6fb1ff"/>
          <circle class="drop" cx="110" cy="30" r="4" fill="#6fb1ff"/>
        </svg>
        <h3>${esc(t("loading"))}</h3>
      </div></div>`);
    const p = S.profile;
    try {
      const [res] = await Promise.all([
        api("recommend", { district: p.district, soil: p.soil, water: p.water, season: p.season }),
        new Promise((r) => setTimeout(r, 1600)),
      ]);
      S.results = res;
      store.set("results", res);
      if (location.hash === "#results") screenResults(); else location.hash = "#results";
    } catch (e) {
      console.error(e);
      location.hash = "#farm/1";
    }
  }

  function countUp(el) {
    const [a, b] = el.dataset.range.split(",").map(Number);
    const t0 = performance.now(), dur = 1100;
    const tick = (now) => {
      const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = `₹${num(Math.round((a * e) / 100) * 100)} – ${num(Math.round((b * e) / 100) * 100)}`;
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function screenResults() {
    const p = S.profile;
    const ready = p.district && p.soil && p.water && p.season;
    if (!ready) {
      render("results", `
        <div class="loading"><div>
          <div style="font-size:80px">🌱</div>
          <h2 style="margin:10px 0 16px">${esc(t("no_profile"))}</h2>
          <button class="btn" data-go="#farm/1">${esc(t("start"))} ➜</button>
        </div></div>`);
      return;
    }
    if (!S.results) { runRecommend(); return; }
    const r = S.results;
    const top = r.crops[0];
    const sayText = `${t("results_title")}: ${r.crops.map((c) => cropName(c.id)).join(", ")}.`;

    const cards = r.crops.map((c, i) => {
      const reasons = c.reasons.map((x) => `<div>✅ ${esc(t("r_" + x.code, { days: num(x.days) }))}</div>`).join("");
      const drops = [1, 2, 3].map((k) => `<span class="${k <= c.drops ? "" : "off"}">💧</span>`).join("");
      const liked = c.community?.good ? `<div class="liked">😊 ${esc(t("liked", { n: num(c.community.good) }))}</div>` : "";
      return `
        <article class="crop">
          <div style="position:relative">
            ${photo(c.id)}
            ${i === 0 ? `<span class="ribbon">⭐ ${esc(t("best"))}</span>` : ""}
            <span class="rank">${i + 1}</span>
          </div>
          <div class="body">
            <div style="display:flex;align-items:center;gap:10px">
              <h3 style="flex:1">${esc(cropName(c.id))}</h3>
              ${speakBtn(`${cropName(c.id)}. ${c.reasons.map((x) => t("r_" + x.code, { days: num(x.days) })).join(". ")}`, "inline")}
            </div>
            <div class="reasons">${reasons}</div>
            <div class="facts">
              <div class="fact"><div class="lbl">${esc(t("water"))}</div><div class="val drops">${drops}</div></div>
              <div class="fact"><div class="lbl">&nbsp;</div><div class="val"><span class="dot ${c.safety}"></span>${esc(t("safety_" + c.safety))}</div></div>
              <div class="fact wide"><div class="lbl">${esc(t("earning"))}</div><div class="val" data-range="${c.earning[0]},${c.earning[1]}">₹0</div></div>
            </div>
            ${liked}
            <button class="btn" data-go="#guide/${c.id}">${esc(t("how_grow"))} ➜</button>
          </div>
        </article>`;
    }).join("");

    render("results", `
      <div class="res-head">
        <div style="display:flex;align-items:center;gap:10px"><h2 style="flex:1">${esc(t("results_title"))}</h2>${speakBtn(sayText, "inline")}</div>
        <div class="profile-chips">
          <span class="chip">📍 ${esc(distName(p.district))}</span>
          <span class="chip">🟫 ${esc(t("soil_" + p.soil))}</span>
          <span class="chip">💧 ${esc(t("water_" + p.water))}</span>
          <span class="chip">📅 ${esc(t("season_" + p.season))}</span>
        </div>
      </div>
      <div class="usual ${r.usual.safety === "safe" ? "ok" : r.usual.safety === "medium" ? "mid" : ""}">
        ${photo(r.usual.id)}
        <div><b>${esc(t("usual_" + ({ risky: "risky", medium: "medium", safe: "ok" })[r.usual.safety], { crop: cropName(r.usual.id) }))}</b></div>
        <span class="dot ${r.usual.safety}" style="margin-left:auto"></span>
      </div>
      <div class="crop-grid">${cards}</div>
      <div class="res-foot">
        <p class="note">${esc(t("approx"))}</p>
        <button class="btn ghost" data-go="#farm/1">✏️ ${esc(t("change"))}</button>
      </div>
    `);
    if (top) S.fb.crop = S.fb.crop || top.id;
    $$("[data-range]", view).forEach((el, i) => setTimeout(() => countUp(el), 350 + i * 150));
  }

  // ---------------------------------------------------------------- guide
  function screenGuide(id) {
    const c = S.meta.crops[id];
    if (!c) { location.hash = "#results"; return; }
    const order = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5];
    const fmt = new Intl.DateTimeFormat(LOCALE[S.lang], { month: "short" });
    const months = order.map((m) => {
      const cls = c.sow.includes(m) ? "sow" : c.harvest.includes(m) ? "har" : "";
      return `<div class="month ${cls}">${esc(fmt.format(new Date(2026, m - 1, 1)))}</div>`;
    }).join("");
    const tips = c.tips.map((tp, i) => `<div class="tip"><div class="n">${i + 1}</div><p>${esc(tp[S.lang])}</p></div>`).join("");
    const sayText = `${c.name[S.lang]}. ${t("days_ready", { days: num(c.days) })}. ${c.tips.map((x) => x[S.lang]).join(" ")}`;
    render("guide", `
      <div class="g-hero">
        ${photo(id)}
        <button class="back-btn" data-go="#results" aria-label="${esc(t("back"))}">←</button>
        ${speakBtn(sayText)}
        <h1>${esc(c.name[S.lang])}</h1>
      </div>
      <div class="guide-body">
        <div class="guide-cal">
          <div class="months">${months}</div>
          <div class="legend">
            <span><i style="background:var(--green-2)"></i>${esc(t("sow"))}</span>
            <span><i style="background:var(--sun)"></i>${esc(t("harvest"))}</span>
            <span>⏱️ ${esc(t("days_ready", { days: num(c.days) }))}</span>
          </div>
        </div>
        <div class="guide-tips">
          <div class="section-t">💡 ${esc(t("tips"))}</div>
          <div>${tips}</div>
        </div>
        <div class="guide-actions">
          <a class="btn call" href="tel:18001801551">📞 ${esc(t("helpline"))} · 1800-180-1551</a>
          <button class="btn ghost" data-ask="${id}">💬 ${esc(t("ask_about"))}</button>
        </div>
      </div>
    `);
  }

  // ---------------------------------------------------------------- feedback
  function screenHarvest() {
    const season = S.profile.season || defaultSeason;
    const ids = Object.keys(S.meta.crops).filter((id) => S.meta.crops[id].season === season);
    if (!S.fb.crop || !ids.includes(S.fb.crop)) S.fb.crop = S.results?.crops?.[0]?.id && ids.includes(S.results.crops[0].id) ? S.results.crops[0].id : null;
    const fb = S.fb;
    render("harvest", `<div class="narrow">
      <div class="q" style="margin-top:12px"><h2>${esc(t("fb_title"))}</h2>${speakBtn(t("fb_title"), "inline")}</div>
      <div class="section-t">🌾 ${esc(t("fb_which"))}</div>
      <div class="fb-crops">${ids.map((id, i) => `
        <button class="fb-crop ${fb.crop === id ? "sel" : ""}" data-fbcrop="${id}" style="animation-delay:${i * 0.04}s">${photo(id)}<span>${esc(cropName(id))}</span></button>`).join("")}
      </div>
      <div class="fb-two"><div>
      <div class="section-t">⚖️ ${esc(t("fb_qty"))}</div>
      <div class="stepper">
        <button data-step="-0.5" aria-label="minus">−</button>
        <div class="val"><b id="qty">${num(fb.quintals)}</b><span>${esc(t("fb_unit"))}</span></div>
        <button data-step="0.5" aria-label="plus">+</button>
      </div>
      </div><div>
      <div class="section-t">🙂 ${esc(t("fb_feel"))}</div>
      <div class="feel">
        ${[["good", "😊"], ["okay", "😐"], ["bad", "😟"]].map(([k, e]) => `<button class="${fb.rating === k ? "sel" : ""}" data-feel="${k}"><span class="e">${e}</span><span>${esc(t(k))}</span></button>`).join("")}
      </div>
      </div></div>
      <button class="btn" id="sendFb" style="margin-top:22px">📤 ${esc(t("send"))}</button>
      <p class="note" id="fbNote">${esc(t("fb_note"))}</p>
    </div>`);
  }

  async function sendFeedback() {
    const fb = S.fb;
    if (!fb.crop || !fb.rating) {
      const n = $("#fbNote", view); n.textContent = t("fb_pick"); n.style.color = "var(--red)"; return;
    }
    const res = await api("feedback", { crop: fb.crop, rating: fb.rating, quintals: fb.quintals, district: S.profile.district, season: S.profile.season });
    S.summary = await api("feedback/summary");
    S.lastThanks = res.summary;
    S.fb = { crop: null, quintals: 5, rating: null };
    location.hash = "#thanks";
  }

  function screenThanks() {
    const district = S.profile.district ? distName(S.profile.district) : "Vidarbha";
    const n = Math.max(1, S.summary?.all_total ?? 1);
    render("thanks", `
      <div class="thanks narrow">
        <div class="big">🎉</div>
        <h1>${esc(t("thanks"))}</h1>
        <p class="muted" style="font-size:19px">${esc(t("thanks_sub", { district }))}</p>
        <div class="community"><div class="faces"><span>😊</span><span>🧑‍🌾</span><span>👩‍🌾</span></div>${esc(t("thanks_count", { n: num(n) }))}</div>
        <button class="btn" data-go="#home" style="margin-top:28px">🏠 ${esc(t("home"))}</button>
      </div>`);
    confetti();
  }

  function confetti() {
    const box = document.createElement("div");
    box.className = "confetti";
    const colors = ["#7cc142", "#f4b400", "#2e8b57", "#f08a24", "#6fb1ff", "#d64545"];
    for (let i = 0; i < 80; i++) {
      const p = document.createElement("i");
      p.style.left = Math.random() * 100 + "%";
      p.style.background = colors[i % colors.length];
      p.style.animationDuration = 1.8 + Math.random() * 1.6 + "s";
      p.style.animationDelay = Math.random() * 0.5 + "s";
      p.style.transform = `rotate(${Math.random() * 360}deg)`;
      box.appendChild(p);
    }
    document.body.appendChild(box);
    setTimeout(() => box.remove(), 4200);
  }

  // ---------------------------------------------------------------- chat
  function setChatMode() {
    const m = S.meta?.chat_mode || "offline";
    $("#chatMode").textContent = t("chat_mode_" + m);
  }
  function renderChips() {
    $("#chatChips").innerHTML = t("chips").map((c) => `<button type="button">${esc(c)}</button>`).join("");
  }
  function addMsg(role, text) {
    const log = $("#chatLog");
    const div = document.createElement("div");
    div.className = "msg " + (role === "user" ? "me" : "bot");
    div.textContent = text;
    if (role !== "user") {
      const b = document.createElement("button");
      b.className = "say"; b.type = "button"; b.textContent = "🔊 " + t("listen");
      b.onclick = () => speak(text, b);
      div.appendChild(document.createElement("br"));
      div.appendChild(b);
    }
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    return div;
  }
  function openChat(prefill) {
    phone.classList.add("chat-open");
    $("#chat").setAttribute("aria-hidden", "false");
    if (!$("#chatLog").children.length) addMsg("bot", t("chat_hello"));
    if (prefill) { $("#chatText").value = prefill; }
    setTimeout(() => $("#chatText").focus({ preventScroll: true }), 350);
  }
  function closeChat() {
    phone.classList.remove("chat-open");
    $("#chat").setAttribute("aria-hidden", "true");
  }
  async function sendChat(text) {
    text = text.trim();
    if (!text) return;
    $("#chatText").value = "";
    addMsg("user", text);
    const typing = document.createElement("div");
    typing.className = "msg bot typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    $("#chatLog").appendChild(typing);
    $("#chatLog").scrollTop = 1e9;
    const p = S.profile;
    try {
      const [res] = await Promise.all([
        api("chat", { message: text, lang: S.lang, profile: p, history: S.chat }),
        new Promise((r) => setTimeout(r, 500)),
      ]);
      typing.remove();
      addMsg("bot", res.reply);
      S.chat.push({ role: "user", text }, { role: "assistant", text: res.reply });
      if (res.mode && S.meta) { S.meta.chat_mode = res.mode; setChatMode(); }
    } catch {
      typing.remove();
      addMsg("bot", "⚠️ " + (S.lang === "en" ? "Could not connect. Please try again." : S.lang === "hi" ? "कनेक्ट नहीं हो पाया. फिर कोशिश करें." : "जोडणी झाली नाही. पुन्हा प्रयत्न करा."));
    }
  }

  $("#chatForm").addEventListener("submit", (e) => { e.preventDefault(); sendChat($("#chatText").value); });
  $("#chatChips").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) sendChat(b.textContent); });
  $("#chatClose").addEventListener("click", () => { history.length > 1 && location.hash === "#chat" ? history.back() : (location.hash = "#" + S.lastRoute); });
  $("#fab").addEventListener("click", () => { location.hash = "#chat"; });

  // voice input
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const mic = $("#micBtn");
  if (!SR) mic.style.display = "none";
  else {
    let rec = null;
    mic.addEventListener("click", () => {
      if (rec) { rec.stop(); return; }
      rec = new SR();
      rec.lang = LOCALE[S.lang];
      rec.interimResults = false;
      rec.onresult = (e) => { const said = e.results[0][0].transcript; sendChat(said); };
      rec.onend = () => { mic.classList.remove("rec"); rec = null; };
      rec.onerror = () => { mic.classList.remove("rec"); rec = null; };
      mic.classList.add("rec");
      rec.start();
    });
  }

  // ---------------------------------------------------------------- events
  view.addEventListener("click", (e) => {
    const go = e.target.closest("[data-go]");
    if (go) { e.preventDefault(); location.hash = go.dataset.go; return; }
    const pk = e.target.closest("[data-pick]");
    if (pk) { pick(pk.dataset.pick, pk.dataset.val, pk); return; }
    const ask = e.target.closest("[data-ask]");
    if (ask) {
      const q = { en: `Tips for ${cropName(ask.dataset.ask)}`, mr: `${cropName(ask.dataset.ask)} साठी टिप्स`, hi: `${cropName(ask.dataset.ask)} के लिए सुझाव` }[S.lang];
      location.hash = "#chat"; setTimeout(() => sendChat(q), 400); return;
    }
    const fc = e.target.closest("[data-fbcrop]");
    if (fc) { S.fb.crop = fc.dataset.fbcrop; $$("[data-fbcrop]", view).forEach((b) => b.classList.toggle("sel", b === fc)); return; }
    const st = e.target.closest("[data-step]");
    if (st) { S.fb.quintals = Math.max(0, Math.min(60, S.fb.quintals + Number(st.dataset.step))); $("#qty", view).textContent = num(S.fb.quintals); return; }
    const fl = e.target.closest("[data-feel]");
    if (fl) { S.fb.rating = fl.dataset.feel; $$("[data-feel]", view).forEach((b) => b.classList.toggle("sel", b === fl)); return; }
    if (e.target.closest("#sendFb")) { sendFeedback(); return; }
    if (e.target.closest("[data-credits]")) { e.preventDefault(); openCredits(); }
  });

  $$(".lang button").forEach((b) => b.addEventListener("click", () => {
    if (S.lang === b.dataset.lang) return;
    S.lang = b.dataset.lang; store.set("lang", S.lang);
    applyStatic();
    route(true);
  }));

  function openCredits() {
    const seen = new Set();
    $("#creditsList").innerHTML = Object.values(window.IMAGES).filter((im) => !seen.has(im.url) && seen.add(im.url))
      .map((im) => `<li>“${esc(im.title)}” — ${esc(im.src)}, ${esc(im.lic)}</li>`).join("");
    $("#credits").classList.add("open");
  }
  $("#creditsClose").addEventListener("click", () => $("#credits").classList.remove("open"));
  $("#footCredits").addEventListener("click", (e) => { e.preventDefault(); openCredits(); });

  // ---------------------------------------------------------------- router
  function route(sameScreen) {
    const h = (location.hash || "#home").slice(1);
    const [name, arg] = h.split("/");
    if (name === "chat") {
      if (!view.children.length) screenHome();
      openChat();
      return;
    }
    closeChat();
    S.lastRoute = h;
    if (sameScreen) prevDepth = DEPTH[name] ?? 0;
    switch (name) {
      case "farm": return screenFarm(Number(arg));
      case "results": return screenResults();
      case "guide": return screenGuide(arg);
      case "harvest": return screenHarvest();
      case "thanks": return screenThanks();
      default: return screenHome();
    }
  }
  window.addEventListener("hashchange", () => route(false));

  // ---------------------------------------------------------------- boot
  (async function boot() {
    try {
      [S.meta, S.summary] = await Promise.all([api("meta"), api("feedback/summary")]);
    } catch (e) {
      view.innerHTML = `<div class="loading"><div><div style="font-size:64px">🔌</div><h3>Server not running. Start it with: python server.py</h3></div></div>`;
      return;
    }
    applyStatic();
    route(true);
    if ("speechSynthesis" in window) window.speechSynthesis.getVoices();
  })();
})();
