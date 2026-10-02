const header = document.querySelector("[data-header]");
const nav = document.querySelector("[data-nav]");
const navToggle = document.querySelector("[data-nav-toggle]");

function updateHeader() {
  header?.classList.toggle("scrolled", window.scrollY > 24);
}

function closeNavigation() {
  nav?.classList.remove("open");
  navToggle?.setAttribute("aria-expanded", "false");
  document.body.style.overflow = "";
}

navToggle?.addEventListener("click", () => {
  const isOpen = nav?.classList.toggle("open");
  navToggle.setAttribute("aria-expanded", String(Boolean(isOpen)));
  document.body.style.overflow = isOpen ? "hidden" : "";
});

nav?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", closeNavigation);
});

window.addEventListener("scroll", updateHeader, { passive: true });
updateHeader();

const revealObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  },
  { threshold: 0.12, rootMargin: "0px 0px -40px" },
);

document.querySelectorAll(".reveal").forEach((element) => {
  revealObserver.observe(element);
});

const year = document.querySelector("[data-year]");
if (year) year.textContent = String(new Date().getFullYear());
