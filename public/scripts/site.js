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

const remembranceFocus = document.querySelector("[data-remembrance-focus]");
const remembranceData = document.querySelector("#remembrance-records");

if (remembranceFocus && remembranceData) {
  try {
    const memorialId = new URLSearchParams(window.location.search).get("memorial");
    const records = JSON.parse(remembranceData.textContent);
    const memorial = records.find((record) => record.id === memorialId);

    if (memorial) {
      const image = remembranceFocus.querySelector("[data-remembrance-image]");
      const placeholder = remembranceFocus.querySelector("[data-remembrance-placeholder]");
      const heart = remembranceFocus.querySelector("[data-remembrance-heart]");
      const kicker = remembranceFocus.querySelector("[data-remembrance-kicker]");
      const name = remembranceFocus.querySelector("[data-remembrance-name]");
      const tagline = remembranceFocus.querySelector("[data-remembrance-tagline]");
      const dates = remembranceFocus.querySelector("[data-remembrance-dates]");
      const note = remembranceFocus.querySelector("[data-remembrance-note]");

      remembranceFocus.hidden = false;
      remembranceFocus.toggleAttribute("data-orphan", memorial.orphan);
      name.textContent = memorial.name;
      tagline.textContent = memorial.tagline;
      dates.textContent = memorial.dates;
      dates.hidden = !memorial.dates;
      kicker.textContent = memorial.orphan ? "Held close by ARSF" : "Remembered together";
      heart.hidden = !memorial.orphan;
      note.textContent = `Although no individual tribute was preserved, ${memorial.name}’s place in the ARSF community is held here with all the others.`;

      if (memorial.image) {
        image.src = memorial.image;
        image.alt = `${memorial.name}, remembered by the ARSF community`;
        image.hidden = false;
        placeholder.hidden = true;
      } else {
        image.hidden = true;
        placeholder.hidden = false;
      }

      document.title = `Remembering ${memorial.name} | Akita Rescue Society of Florida`;
    }
  } catch {
    // The shared remembrance remains complete if contextual data is unavailable.
  }
}
