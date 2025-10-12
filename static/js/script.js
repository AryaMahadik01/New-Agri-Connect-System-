// ✅ Toast auto-remove
document.addEventListener("DOMContentLoaded", () => {
  const toasts = document.querySelectorAll(".toast");
  toasts.forEach((toast) => {
    setTimeout(() => {
      toast.remove();
    }, 4000); // 4 seconds
  });
});

// ✅ Navbar dropdown
(function () {
  const btn = document.getElementById("navUserBtn");
  const wrapper = btn && btn.closest(".nav-user-wrapper");

  function closeDropdown() {
    if (wrapper) wrapper.classList.remove("open");
    if (btn) btn.setAttribute("aria-expanded", "false");
    const dropdown = document.getElementById("navUserDropdown");
    if (dropdown) dropdown.setAttribute("aria-hidden", "true");
  }

  function toggleDropdown(e) {
    e.stopPropagation();
    if (!wrapper) return;
    wrapper.classList.toggle("open");
    const isOpen = wrapper.classList.contains("open");
    btn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    const dropdown = document.getElementById("navUserDropdown");
    if (dropdown) dropdown.setAttribute("aria-hidden", isOpen ? "false" : "true");
  }

  if (btn) {
    btn.addEventListener("click", toggleDropdown);

    // close on Esc
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape") closeDropdown();
    });

    // close on outside click
    document.addEventListener("click", (ev) => {
      if (!wrapper) return;
      if (!wrapper.contains(ev.target)) closeDropdown();
    });
  }
})();

function updateQuantity(productId, change) {
  const qtySpan = document.getElementById(`qty-${productId}`);
  let qty = parseInt(qtySpan.innerText);
  qty = Math.max(1, qty + change); // Prevent 0 or negative

  qtySpan.innerText = qty;

  // Update item total
  const price = parseInt(document.querySelector(`#total-${productId}`).getAttribute("data-price") || 0);
  document.getElementById(`total-${productId}`).innerText = qty * price;

  // TODO: Optionally send AJAX request to backend to update DB
}

// 🌟 Customer Review Slider
document.addEventListener("DOMContentLoaded", function () {
  const slider = document.querySelector(".review-slider");
  const nextBtn = document.querySelector(".next-btn");
  const prevBtn = document.querySelector(".prev-btn");

  if (slider && nextBtn && prevBtn) {
    let scrollAmount = 0;
    const slideWidth = 340; // width + gap

    nextBtn.addEventListener("click", () => {
      slider.scrollBy({ left: slideWidth, behavior: "smooth" });
    });

    prevBtn.addEventListener("click", () => {
      slider.scrollBy({ left: -slideWidth, behavior: "smooth" });
    });

    // Auto slide
    setInterval(() => {
      slider.scrollBy({ left: slideWidth, behavior: "smooth" });
    }, 3000);
  }
});

// 🌍 Safe multilingual translation with fallback + persistence
document.addEventListener("DOMContentLoaded", () => {
  const langSelect = document.getElementById("languageSelect");
  if (!langSelect) return;

  // Remember last selected language
  const savedLang = localStorage.getItem("preferredLang");
  if (savedLang) langSelect.value = savedLang;

  langSelect.addEventListener("change", async () => {
    const lang = langSelect.value;
    localStorage.setItem("preferredLang", lang);

    const elements = document.querySelectorAll("h1, h2, h3, p, a, button, label, span");

    // ✅ If English selected — restore all original text instantly
    if (lang === "en") {
      elements.forEach(el => {
        if (el.dataset.original) el.innerText = el.dataset.original;
      });
      return;
    }

    // 🌐 Translate every visible text element
    for (const el of elements) {
      const original = el.dataset.original || el.innerText.trim();
      if (!original || original.length < 2) continue;

      // Save original text (only once)
      if (!el.dataset.original) el.dataset.original = original;

      try {
        const response = await fetch("/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: original, lang }),
        });
        const data = await response.json();
        const translated = data.translated?.trim();

        // ✅ Use translation only if it's valid
        if (
          translated &&
          translated.length > 1 &&
          !translated.toUpperCase().includes("PLEASE SELECT TWO DISTINCT LANGUAGES")
        ) {
          el.innerText = translated;
        } else {
          el.innerText = original;
        }
      } catch (err) {
        console.warn("Translation failed for:", original, err);
        el.innerText = original;
      }
    }
  });
});



