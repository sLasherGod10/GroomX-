/**
 * GroomX v6 — API Client
 * Drop this file next to your groomx_v6.html
 * It replaces all localStorage calls with real Flask+MongoDB API calls.
 *
 * Usage: add  <script src="groomx_api.js"></script>
 *        BEFORE the closing </body> tag in groomx_v6.html
 */

const API = {
  BASE: "http://localhost:5000/api",   // ← change if Flask runs elsewhere
  _token: sessionStorage.getItem("gx_token") || "",

  // ── Helpers ────────────────────────────────────────────────────────────────

  _headers() {
    const h = { "Content-Type": "application/json" };
    if (this._token) h["Authorization"] = "Bearer " + this._token;
    return h;
  },

  async _req(method, path, body = null) {
    const opts = { method, headers: this._headers() };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res  = await fetch(this.BASE + path, opts);
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "API error");
      return json.data ?? json;
    } catch (e) {
      console.warn("[GroomX API]", method, path, e.message);
      throw e;
    }
  },

  get:    (p)       => API._req("GET",    p),
  post:   (p, b)    => API._req("POST",   p, b),
  patch:  (p, b)    => API._req("PATCH",  p, b),
  delete: (p)       => API._req("DELETE", p),

  setToken(tok) {
    this._token = tok;
    sessionStorage.setItem("gx_token", tok);
  },
  clearToken() {
    this._token = "";
    sessionStorage.removeItem("gx_token");
  },

  // ── Auth ───────────────────────────────────────────────────────────────────

  auth: {
    register: (d)    => API.post("/auth/register", d),
    login:    (d)    => API.post("/auth/login", d),
    demo:     (role) => API.post("/auth/demo", { role }),
    me:       ()     => API.get("/auth/me"),
    logout:   ()     => API.post("/auth/logout"),
  },

  // ── Bookings ───────────────────────────────────────────────────────────────

  bookings: {
    list:    (q = {})    => API.get("/bookings/?" + new URLSearchParams(q)),
    create:  (d)         => API.post("/bookings/", d),
    get:     (id)        => API.get(`/bookings/${id}`),
    update:  (id, d)     => API.patch(`/bookings/${id}`, d),
    delete:  (id)        => API.delete(`/bookings/${id}`),
    slots:   (date, sty) => API.get(`/bookings/slots?date=${date}&stylist=${sty}`),
  },

  // ── Home Visits ────────────────────────────────────────────────────────────

  homeVisits: {
    list:    (q = {})         => API.get("/home-visits/?" + new URLSearchParams(q)),
    create:  (d)              => API.post("/home-visits/", d),
    get:     (id)             => API.get(`/home-visits/${id}`),
    update:  (id, d)          => API.patch(`/home-visits/${id}`, d),
    delete:  (id)             => API.delete(`/home-visits/${id}`),
    calcFee: (dist, service)  => API.get(`/home-visits/calculate-fee?distance_km=${dist}&service=${encodeURIComponent(service)}`),
  },

  // ── Beard Styles ───────────────────────────────────────────────────────────

  beardStyles: {
    list: (cat = "") => API.get("/beard-styles/" + (cat ? "?category=" + cat : "")),
    get:  (id)       => API.get(`/beard-styles/${id}`),
  },

  // ── Salons ─────────────────────────────────────────────────────────────────

  salons: {
    list:   (q = {}) => API.get("/salons/?" + new URLSearchParams(q)),
    get:    (id)     => API.get(`/salons/${id}`),
    update: (id, d)  => API.patch(`/salons/${id}`, d),
  },

  // ── AI Scans ───────────────────────────────────────────────────────────────

  aiScans: {
    log:   (shape, conf, cuts) => API.post("/ai-scans/log", { shape, confidence: conf, top_cuts: cuts }),
    list:  ()                  => API.get("/ai-scans/"),
    stats: ()                  => API.get("/ai-scans/stats"),
  },

  // ── Dashboard ──────────────────────────────────────────────────────────────

  dashboard: {
    stats:    ()   => API.get("/dashboard/stats"),
    charts:   ()   => API.get("/dashboard/charts"),
    pending:  ()   => API.get("/dashboard/pending"),
    accept:   (id) => API.post(`/dashboard/pending/${id}/accept`),
    decline:  (id) => API.post(`/dashboard/pending/${id}/decline`),
  },
};


// ══════════════════════════════════════════════════════════════════════════════
// OVERRIDE GROOMX v6 FUNCTIONS TO USE THE REAL API
// These replace the localStorage-based implementations in groomx_v6.html
// ══════════════════════════════════════════════════════════════════════════════

// ── AUTH overrides ────────────────────────────────────────────────────────────

window.doLogin = async function() {
  const email = document.getElementById("lE").value.trim();
  const pass  = document.getElementById("lP").value;
  try {
    const res = await API.auth.login({ email, password: pass });
    API.setToken(res.token);
    CU = res.user;
    applyLogin();
    notify("success", "✦ Welcome", "Signed in as " + res.user.name);
  } catch (e) {
    notify("error", "Access Denied", e.message);
  }
};

window.demoLogin = async function(role) {
  try {
    const res = await API.auth.demo(role);
    API.setToken(res.token);
    CU = res.user;
    applyLogin();
    notify("info", "✦ Demo Mode", "Signed in as " + role);
  } catch (e) {
    notify("error", "Demo Error", e.message);
  }
};

window.doReg = async function() {
  const name       = document.getElementById("rN").value.trim();
  const email      = document.getElementById("rE").value.trim();
  const password   = document.getElementById("rPw").value;
  const salon_name = document.getElementById("rSN")?.value || "";
  try {
    const res = await API.auth.register({ name, email, password, role: regRole, salon_name });
    API.setToken(res.token);
    CU = res.user;
    applyLogin();
    notify("success", "✦ Welcome", "Account created, " + name);
  } catch (e) {
    notify("error", "Registration Failed", e.message);
  }
};

window.logout = function() {
  API.auth.logout().catch(() => {});
  API.clearToken();
  CU = null;
  showLogin();
  notify("info", "✦ Farewell", "See you at the studio!");
};

// ── BOOKING overrides ─────────────────────────────────────────────────────────

window.confBook = async function() {
  const sv   = document.getElementById("bNm")?.value?.trim();
  const ph   = document.getElementById("bPh")?.value?.trim();
  const svcV = document.getElementById("bSv")?.value || "";
  const dt   = document.getElementById("bDt")?.value;
  const svcN = svcV.split("—")[0]?.trim() || "";

  // Client-side guard so user gets instant feedback
  if (!sv || !ph || !svcN || !selSt || !dt || !selSl) {
    notify("error", "Missing Details", "Please fill in all fields and select a stylist & time slot.");
    return;
  }

  try {
    const bk = await API.bookings.create({
      name:    sv,
      phone:   ph,
      service: svcN,
      stylist: selSt,
      date:    dt,
      time:    selSl,
    });
    toast("✦ Booking received · " + bk.booking_id);
    notify("success", "✦ Booked!", bk.name + " · " + bk.service + " · " + bk.booking_id);
    selSt = ""; selSl = "";
    nStep(1);
    document.getElementById("bNm").value = "";
    document.getElementById("bSv").value = "";
    syncBSum();
    // Go to dashboard and force a fresh load from the API
    setTimeout(() => { go("db"); setTimeout(renderDB, 400); }, 1200);
  } catch (e) {
    notify("error", "Booking Failed", e.message);
  }
};

// Load real-time slot availability from backend
window._origNStep = window.nStep;
window.nStep = async function(s) {
  if (s === 3) {
    const date = document.getElementById("bDt").value;
    const sty  = selSt;
    if (date && sty) {
      try {
        const res = await API.bookings.slots(date, sty);
        const slots = res.slots || [];
        // Rebuild taken list from API
        window.TAKEN = slots.filter(sl => !sl.available).map(sl => sl.time);
        renderSlots(); // re-render with real data
      } catch (e) {
        console.warn("Could not load slots from API — using local fallback");
      }
    }
  }
  _origNStep(s);
};

// ── HOME VISIT overrides ──────────────────────────────────────────────────────

window.confirmHomeAppt = async function() {
  const svc = document.getElementById("hSv").value;
  const svcN = svc.split("—")[0]?.trim() || "";

  try {
    const visit = await API.homeVisits.create({
      name:        document.getElementById("hNm").value,
      phone:       document.getElementById("hPh").value,
      service:     svcN,
      address:     document.getElementById("hAd").value,
      landmark:    document.getElementById("hLm").value || "",
      date:        document.getElementById("hDt").value,
      time:        document.getElementById("hTm").value,
      distance_km: parseFloat(document.getElementById("dSlider").value) || 5,
    });
    toast("✦ Home visit confirmed · " + visit.visit_id);
    notify("success", "✦ Home Visit Booked!", svcN + " on " + visit.date);
    setTimeout(() => { go("db"); setTimeout(renderDB, 400); }, 1200);
  } catch (e) {
    notify("error", "Booking Failed", e.message);
  }
};

// Live travel fee from API
window.updDist = async function() {
  const d = parseInt(document.getElementById("dSlider").value);
  document.getElementById("dVal").textContent = d + " km";
  document.getElementById("dWarn").style.display = d > 10 ? "block" : "none";

  const svc = document.getElementById("hSv").value;
  const svcN = svc.split("—")[0]?.trim() || "";

  if (svcN) {
    try {
      const fee = await API.homeVisits.calcFee(d, svcN);
      document.getElementById("hSTr").textContent  = "₹" + fee.travel_fee;
      document.getElementById("hSSc").textContent  = "₹" + fee.service_fee;
      document.getElementById("hSTot").textContent = "₹" + fee.total.toLocaleString("en-IN");
      document.getElementById("chargeNote").textContent = fee.note;
    } catch (_) { /* fallback to local calc */ }
  }
  syncHSum();
};

// ── AI SCAN override ──────────────────────────────────────────────────────────

const _origShowAIRes = window.showAIRes;
window.showAIRes = function(shape, conf) {
  // Still show the UI (unchanged)
  _origShowAIRes(shape, conf);
  // Also log to backend
  if (API._token) {
    API.aiScans.log(shape, conf, []).catch(() => {});
  }
};

// ── DASHBOARD overrides ───────────────────────────────────────────────────────

window.renderDB = async function() {
  // ── Stats & charts ──────────────────────────────────────────
  try {
    const [stats, charts] = await Promise.all([
      API.dashboard.stats(),
      API.dashboard.charts(),
    ]);

    const el = (id) => document.getElementById(id);
    if (el("st1")) el("st1").textContent = (stats.total_bookings || 0) + (stats.total_home_visits || 0);
    if (el("st2")) el("st2").textContent = "₹" + (stats.today_revenue || 0).toLocaleString("en-IN");
    if (el("st2c")) el("st2c").textContent = (stats.pending_bookings || 0) + " pending";
    if (el("st3")) el("st3").textContent = stats.total_home_visits || 0;
    if (el("st4")) el("st4").textContent = stats.ai_scans || 0;

    if (charts.by_day)     renderBar(charts.by_day);
    if (charts.by_service) {
      const byS = {};
      Object.entries(charts.by_service).forEach(([k, v]) => byS[k] = v.count);
      renderPie(byS);
    }
  } catch (e) {
    console.warn("[GroomX] Stats/charts API error:", e.message);
    // Fallback: show localStorage counts
    try {
      const s = DB.stats();
      aniCtr("st1", s.total);
      document.getElementById("st2").textContent = "₹" + s.rev.toLocaleString("en-IN");
      renderBar(s.byD);
      renderPie(s.byS);
    } catch (_) {}
  }

  // ── Bookings table ──────────────────────────────────────────
  try {
    const activeFilter = document.querySelector(".tFilt.on")?.dataset?.filter || "all";
    const [bks, hvs] = await Promise.all([
      API.bookings.list(activeFilter !== "all" && activeFilter !== "home" ? {status: activeFilter} : {}),
      API.homeVisits.list(activeFilter !== "all" && activeFilter !== "home" ? {status: activeFilter} : {}),
    ]);

    let combined = [...(bks || []), ...(hvs || [])];

    // Apply client-side filter for "Home Visit" tab
    if (activeFilter === "home") combined = combined.filter(b => b.type === "home");

    // Sort newest first
    combined.sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));

    _renderTable(combined);
  } catch (e) {
    console.warn("[GroomX] Bookings table API error:", e.message);
    // Fallback: render from localStorage
    try { renderTbl(); } catch (_) {}
  }
};

// Table rendering for real API data
function _renderTable(data) {
  const q    = (document.getElementById("tSrch")?.value || "").toLowerCase();
  let rows   = data;
  if (q) rows = rows.filter(b =>
    (b.name || "").toLowerCase().includes(q) ||
    (b.service || "").toLowerCase().includes(q) ||
    (b.booking_id || b.visit_id || "").toLowerCase().includes(q)
  );
  document.getElementById("tCnt").textContent = rows.length + " records";
  document.getElementById("dbBody").innerHTML = rows.length
    ? rows.map(b => {
        const id     = b.booking_id || b.visit_id || "";
        const isHome = b.type === "home";
        const price  = isHome ? ("₹" + (b.total_price || b.price || 0).toLocaleString("en-IN")) : ("₹" + (b.price || 0).toLocaleString("en-IN"));
        return `<tr>
          <td class="tid">${id}</td>
          <td>${b.name || "—"}</td>
          <td>${b.service || "—"}</td>
          <td><span class="bdg ${isHome ? "home" : "confirmed"}">${isHome ? "Home Visit" : "Studio"}</span></td>
          <td>${b.stylist || "—"}</td>
          <td style="font-family:'Cormorant Garamond',serif;font-style:italic;color:var(--muted)">${b.date || "—"}</td>
          <td style="color:var(--gold3)">${b.time || "—"}</td>
          <td style="color:var(--gold2);font-family:'Playfair Display',serif">${price}</td>
          <td><span class="bdg ${b.status}">${b.status || "—"}</span></td>
          <td><div style="display:flex;gap:4px">
            <button class="ra2" onclick="viewRowAPI('${id}','${isHome}')">View</button>
            <button class="ra2" onclick="updateStatusAPI('${id}','${isHome}','completed')">✓</button>
            <button class="ra2 del" onclick="deleteRowAPI('${id}','${isHome}')">✕</button>
          </div></td>
        </tr>`;
      }).join("")
    : `<tr><td colspan="10" style="text-align:center;padding:36px;font-family:'Cormorant Garamond',serif;font-style:italic;color:var(--muted)">No records found</td></tr>`;
}

window.updateStatusAPI = async function(id, isHome, status) {
  try {
    if (isHome === "true") await API.homeVisits.update(id, { status });
    else                    await API.bookings.update(id, { status });
    renderDB();
    notify("info", "✦ Updated", "Status changed to " + status);
  } catch (e) { notify("error", "Update Failed", e.message); }
};

window.deleteRowAPI = async function(id, isHome) {
  if (!confirm("Delete record " + id + "?")) return;
  try {
    if (isHome === "true") await API.homeVisits.delete(id);
    else                    await API.bookings.delete(id);
    renderDB();
    notify("warning", "Deleted", "Record removed");
  } catch (e) { notify("error", "Delete Failed", e.message); }
};

window.viewRowAPI = async function(id, isHome) {
  try {
    const b = isHome === "true"
      ? await API.homeVisits.get(id)
      : await API.bookings.get(id);

    document.getElementById("modContent").innerHTML = `
      <div style="font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:900;color:var(--gold2);margin-bottom:4px">${id}</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:.75rem;font-style:italic;color:var(--muted);margin-bottom:18px">${b.created_at || ""}</div>
      <div style="background:rgba(201,146,42,.04);border:1px solid rgba(201,146,42,.1);border-radius:12px;padding:16px">
        ${Object.entries({Name:b.name,Phone:b.phone||"—",Service:b.service,Type:(b.type||"studio").toUpperCase(),Stylist:b.stylist||"—",Date:b.date,Time:b.time,Price:b.price||b.total_price,Status:b.status})
          .map(([k,v])=>`<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(201,146,42,.06);font-size:.82rem">
            <span style="font-family:'DM Sans',sans-serif;font-size:.58rem;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:var(--muted)">${k}</span>
            <span style="font-family:'Cormorant Garamond',serif;font-size:.95rem;color:var(--cream)">${v||"—"}</span></div>`).join("")}
      </div>`;
    document.getElementById("modAct").textContent = "Cancel Booking";
    document.getElementById("modAct").onclick = () => {
      updateStatusAPI(id, isHome, "cancelled");
      closeMod();
    };
    document.getElementById("modOv").classList.add("show");
  } catch (e) { notify("error", "Load Failed", e.message); }
};

// ── OWNER PANEL overrides ─────────────────────────────────────────────────────

window.renderOwner = async function() {
  try {
    const [stats, pendingRes] = await Promise.all([
      API.dashboard.stats(),
      API.dashboard.pending(),
    ]);
    document.getElementById("owP").textContent  = pendingRes.total_pending || 0;
    document.getElementById("owC").textContent  = stats.total_bookings - (stats.total_pending || 0);
    document.getElementById("owR").textContent  = "₹" + (stats.today_revenue || 0).toLocaleString("en-IN");
    document.getElementById("owCL").textContent = stats.unique_clients || 0;

    const pending = pendingRes.pending || [];
    document.getElementById("reqBody").innerHTML = pending.length
      ? pending.map(b => {
          const id = b.booking_id || b.visit_id || "";
          return `<div class="req-row" id="rr_${id}">
            <div class="req-av">${b.type === "home" ? "🏠" : "✂"}</div>
            <div class="req-info">
              <div class="req-nm">${b.name} <span style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.72rem;color:var(--muted)">· ${id}</span></div>
              <div class="req-dt">${b.service} · ${b.date} · ${b.time} · ₹${b.price || b.total_price || 0}${b.type === "home" ? " · Home Visit" : ""}</div>
            </div>
            <div style="display:flex;gap:6px">
              <button class="ra" onclick="acceptReqAPI('${id}')">✓ Accept</button>
              <button class="rd" onclick="declineReqAPI('${id}')">✕ Decline</button>
            </div>
          </div>`;
        }).join("")
      : `<div style="padding:28px;text-align:center;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.95rem;color:var(--muted)">No pending requests at this time</div>`;
  } catch (e) {
    console.warn("Owner panel API error:", e.message);
    // graceful fallback — call original local renderOwner logic
  }
};

window.acceptReqAPI = async function(id) {
  try {
    await API.dashboard.accept(id);
    document.getElementById("rr_" + id)?.remove();
    notify("success", "✦ Accepted", "Appointment confirmed");
    renderOwner();
  } catch (e) { notify("error", "Error", e.message); }
};

window.declineReqAPI = async function(id) {
  try {
    await API.dashboard.decline(id);
    document.getElementById("rr_" + id)?.remove();
    notify("warning", "Declined", "Appointment declined");
    renderOwner();
  } catch (e) { notify("error", "Error", e.message); }
};

window.acceptAll = async function() {
  try {
    const res = await API.dashboard.pending();
    const ids = (res.pending || []).map(b => b.booking_id || b.visit_id);
    await Promise.all(ids.map(id => API.dashboard.accept(id)));
    notify("success", "✦ All Confirmed", "All pending appointments accepted");
    renderOwner();
  } catch (e) { notify("error", "Error", e.message); }
};

// ── SALON FINDER overrides ────────────────────────────────────────────────────

window.renderSalonList = async function() {
  const q = (document.getElementById("mapSrch")?.value || "").toLowerCase();
  const params = {};
  if (mFilt === "open")    params.open = "true";
  if (mFilt === "home")    params.home_visit = "true";
  if (mFilt === "premium") params.min_rating = "4.7";
  if (q) params.search = q;

  try {
    const res  = await API.salons.list(params);
    const data = res.salons || [];
    document.getElementById("sCnt").textContent = data.length + " studios found";
    document.getElementById("salonLst").innerHTML = data.map(s => `
      <div class="s-item ${selS === s.salon_id ? "sel" : ""}" id="si_${s.salon_id}" onclick="selectS_API('${s.salon_id}')">
        <div class="s-nm">${s.name}</div>
        <div class="s-ad">${s.address}</div>
        <div class="s-meta">
          <span class="s-dist">✦ ${s.distance_km} km</span>
          <span class="s-rat">★ ${s.rating}</span>
          <span class="s-open ${s.is_open ? "o" : "c"}">${s.is_open ? "Open" : "Closed"}</span>
          ${s.home_visit ? '<span style="font-family:\'Cormorant Garamond\',serif;font-style:italic;font-size:.65rem;color:var(--gold3)">Home visit</span>' : ""}
        </div>
      </div>`).join("");
  } catch (e) {
    console.warn("Salon list API error — using static data");
    // Will fall through to the original static renderSalonList
  }
};

window.selectS_API = async function(salonId) {
  selS = salonId;
  try {
    const s = await API.salons.get(salonId);
    document.querySelectorAll(".s-item").forEach(el => el.classList.remove("sel"));
    document.getElementById("si_" + salonId)?.classList.add("sel");
    document.getElementById("si_" + salonId)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    document.querySelectorAll(".mpin").forEach(p => p.classList.remove("sel"));
    document.getElementById("p_" + salonId)?.classList.add("sel");

    const det = document.getElementById("mapDet");
    document.getElementById("mapDetC").innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
        <div>
          <div style="font-family:'Playfair Display',serif;font-weight:700;font-size:.9rem;color:var(--cream)">${s.name}</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:.72rem;font-style:italic;color:var(--muted);margin-top:2px">
            ${s.address} · ${s.distance_km} km · ★ ${s.rating} ·
            ${s.is_open ? `<span style="color:#70d090">Open</span>` : `<span style="color:#e08070">Closed</span>`}
            · ${s.hours}
          </div>
        </div>
        <div style="display:flex;gap:7px">
          <button class="btn btn-gold btn-xs" onclick="go('booking')">Book Here</button>
          <button class="btn btn-outline btn-xs" onclick="notify('info','📞 Calling','${s.phone}')">📞 Call</button>
          ${s.home_visit ? `<button class="btn btn-outline btn-xs" onclick="go('homeappt')">🏠 Visit</button>` : ""}
        </div>
      </div>`;
    det.classList.add("show");
  } catch (e) {
    console.warn("Salon detail error:", e.message);
  }
};

// ── EXPORT CSV (real data) ────────────────────────────────────────────────────

window.exportCSV = async function() {
  try {
    const [bks, hvs] = await Promise.all([
      API.bookings.list(),
      API.homeVisits.list(),
    ]);
    const all = [...(bks || []), ...(hvs || [])];
    const header = "ID,Name,Phone,Service,Type,Stylist,Date,Time,Price,Status";
    const rows   = all.map(b => [
      b.booking_id || b.visit_id, b.name, b.phone, b.service,
      b.type, b.stylist, b.date, b.time, b.price || b.total_price, b.status
    ].join(","));
    const blob = new Blob([[header, ...rows].join("\n")], { type: "text/csv" });
    const a    = document.createElement("a");
    a.href     = URL.createObjectURL(blob);
    a.download = "groomx_bookings.csv";
    a.click();
    notify("success", "✦ Exported", all.length + " records downloaded");
  } catch (e) {
    notify("error", "Export Failed", e.message);
  }
};

// ── Connection status indicator ───────────────────────────────────────────────

(async function checkBackend() {
  try {
    const res = await fetch("http://localhost:5000/", { method: "GET" });
    if (res.ok) {
      console.log("%c✦ GroomX Backend Connected ✦", "color:#c9922a;font-size:14px;font-weight:bold");
    }
  } catch (_) {
    console.warn("⚠ GroomX Backend not reachable — running in offline/localStorage mode");
    // Show a subtle banner
    const banner = document.createElement("div");
    banner.style.cssText = "position:fixed;bottom:0;left:0;right:0;background:rgba(30,15,5,.95);border-top:1px solid rgba(201,146,42,.3);padding:8px 20px;text-align:center;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.82rem;color:rgba(201,146,42,.7);z-index:9990";
    banner.textContent = "⚠ Running in offline mode — start Flask backend to enable full database features";
    document.body.appendChild(banner);
    setTimeout(() => banner.remove(), 6000);
  }
})();

console.log("%c✦ GroomX API Client v6 Loaded ✦", "color:#f0c060;font-size:12px");
