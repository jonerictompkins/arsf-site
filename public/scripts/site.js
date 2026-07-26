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
    if (window.innerWidth >= 1051) {
      closeMenu();
    }
  });
}

const archiveFilter = document.querySelector("[data-archive-filter]");
const filterGrid = document.querySelector("[data-filter-grid]");
const filterStatus = document.querySelector("[data-filter-status]");

if (archiveFilter && filterGrid) {
  const items = [...filterGrid.children];

  const updateFilter = () => {
    const query = archiveFilter.value.trim().toLocaleLowerCase();
    let visible = 0;

    for (const item of items) {
      const searchable = (item.dataset.search || item.textContent).toLocaleLowerCase();
      const matches = !query || searchable.includes(query);
      item.toggleAttribute("data-filter-hidden", !matches);
      if (matches) {
        visible += 1;
      }
    }

    if (filterStatus) {
      filterStatus.textContent = query
        ? `${visible} of ${items.length} shown`
        : `${items.length} entries`;
    }
  };

  archiveFilter.addEventListener("input", updateFilter);
  updateFilter();
}
