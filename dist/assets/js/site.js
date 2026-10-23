(function () {
  "use strict";

  // Mobile navigation
  var btn = document.querySelector(".nav-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    var setOpen = function (open) {
      btn.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("open", open);
      document.body.classList.toggle("nav-open", open);
    };
    btn.addEventListener("click", function () { setOpen(btn.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setOpen(false); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
  }

  // Enquiry form
  var form = document.getElementById("enquiry");
  if (!form) return;
  var status = form.querySelector(".form-status");
  var F = function (n) { return form.elements.namedItem(n); };
  var params = new URLSearchParams(location.search);
  var t = params.get("type");
  if (t) { var r = form.querySelector('input[name="type"][value="' + t + '"]'); if (r) r.checked = true; }
  var p = params.get("product");
  if (p) F("message").value = "Product: " + p.slice(0, 120) + "\n";

  var via = "wa";
  form.querySelectorAll("button[data-via]").forEach(function (b) {
    b.addEventListener("click", function () { via = b.getAttribute("data-via"); });
  });

  function setErr(el, msg) {
    var id = el.id + "-err";
    var old = document.getElementById(id);
    if (old) old.remove();
    if (msg) {
      el.setAttribute("aria-invalid", "true");
      el.setAttribute("aria-describedby", id);
      var s = document.createElement("span");
      s.className = "err"; s.id = id; s.textContent = msg;
      el.insertAdjacentElement("afterend", s);
    } else {
      el.removeAttribute("aria-invalid");
      el.removeAttribute("aria-describedby");
    }
  }

  function validate() {
    var ok = true, first = null;
    [["name", "Please enter your name."], ["company", "Please enter your business name."], ["city", "Please enter your city or country."]].forEach(function (f) {
      var el = F(f[0]);
      var bad = el.value.trim().length < 2;
      setErr(el, bad ? f[1] : "");
      if (bad) { ok = false; first = first || el; }
    });
    var ph = F("phone"), digits = ph.value.replace(/[^\d]/g, "");
    var phBad = digits.length < 8 || digits.length > 15;
    setErr(ph, phBad ? "Please enter a valid phone number with country code if outside India." : "");
    if (phBad) { ok = false; first = first || ph; }
    var em = F("email");
    var emBad = em.value.trim() !== "" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em.value.trim());
    setErr(em, emBad ? "Please enter a valid email address or leave it blank." : "");
    if (emBad) { ok = false; first = first || em; }
    if (first) first.focus();
    return ok;
  }

  function compose() {
    var type = form.querySelector('input[name="type"]:checked').value;
    var label = { quote: "Quote request", catalogue: "Catalogue request", general: "Business enquiry" }[type];
    var interests = Array.prototype.map.call(form.querySelectorAll('input[name="interest"]:checked'), function (c) { return c.value; });
    var lines = [
      label + " — via website",
      "Name: " + F("name").value.trim(),
      "Business: " + F("company").value.trim(),
      F("btype").value ? "Business type: " + F("btype").value : "",
      "Location: " + F("city").value.trim(),
      "Phone: " + F("phone").value.trim(),
      F("email").value.trim() ? "Email: " + F("email").value.trim() : "",
      interests.length ? "Interested in: " + interests.join(", ") : "",
      F("message").value.trim() ? "Requirements: " + F("message").value.trim() : ""
    ].filter(Boolean);
    return { subject: label + " — " + F("company").value.trim(), body: lines.join("\n") };
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    status.className = "form-status"; status.textContent = "";
    if (F("botcheck").value) return; // bot trap
    if (!validate()) { status.className = "form-status bad"; status.textContent = "Please check the highlighted fields."; return; }
    var m = compose();
    var key = form.getAttribute("data-key");

    if (key) {
      // Optional server-side copy via Web3Forms (only if an access key is configured)
      var fd = new FormData();
      fd.append("access_key", key); fd.append("subject", m.subject); fd.append("from_name", "Website enquiry");
      fd.append("message", m.body); fd.append("botcheck", "");
      if (F("email").value.trim()) fd.append("replyto", F("email").value.trim());
      fetch("https://api.web3forms.com/submit", { method: "POST", body: fd }).catch(function () {});
    }

    if (via === "email") {
      location.href = "mailto:" + form.getAttribute("data-email") + "?subject=" + encodeURIComponent(m.subject) + "&body=" + encodeURIComponent(m.body);
      status.className = "form-status ok";
      status.textContent = "Your email app should open with the message ready — please press Send there. If it doesn't open, email us at " + form.getAttribute("data-email") + ".";
    } else {
      var url = "https://wa.me/" + form.getAttribute("data-wa") + "?text=" + encodeURIComponent(m.body);
      var w = window.open(url, "_blank");
      if (w) { try { w.opener = null; } catch (err) {} } else { location.href = url; }
      status.className = "form-status ok";
      status.textContent = "WhatsApp has opened with your enquiry pre-filled — please press Send there to reach our team.";
    }
  });
})();
