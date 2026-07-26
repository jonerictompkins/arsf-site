const toggle = document.querySelector(".menu-toggle");
const navigation = document.querySelector(".primary-nav");

if (toggle && navigation) {
  const closeMenu = () => {
    toggle.setAttribute("aria-expanded", "false");
    navigation.removeAttribute("data-open");
  };

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isOpen));
    navigation.toggleAttribute("data-open", !isOpen);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      closeMenu();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 860) {
      closeMenu();
    }
  });
}
