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
