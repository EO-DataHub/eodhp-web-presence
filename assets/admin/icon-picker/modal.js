import { loadIcons } from "./icons.js";

const PAGE_SIZE = 200;
const SEARCH_DEBOUNCE_MS = 120;

const cellHtml = (i) =>
  `<button type="button" class="mdi-picker__cell" data-name="${i.name}" title="${i.name}" role="option">
     <i class="mdi mdi-${i.name}" aria-hidden="true"></i>
     <span class="mdi-picker__cell-name">${i.name}</span>
   </button>`;

export function openIconModal() {
  return new Promise((resolve) => {
    const dialog = document.createElement("div");
    dialog.className = "w-dialog";
    dialog.setAttribute("aria-hidden", "true");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-label", "Insert Material Design icon");
    dialog.innerHTML = `
      <div class="w-dialog__overlay"></div>
      <div class="w-dialog__box">
        <div class="mdi-picker">
          <div class="mdi-picker__header">
            <h2 class="mdi-picker__title">Insert Material Design icon</h2>
            <button type="button" class="mdi-picker__close" aria-label="Close">&times;</button>
          </div>
          <div class="mdi-picker__controls">
            <input type="search" class="mdi-picker__search" placeholder="Search icons (e.g. heart, recycle, leaf)" aria-label="Search icons" />
            <div class="mdi-picker__sizes">
              <button type="button" class="mdi-picker__size" data-size="sm" aria-pressed="true" title="Small (1em)">S</button>
              <button type="button" class="mdi-picker__size" data-size="md" aria-pressed="false" title="Medium (1.5em)">M</button>
              <button type="button" class="mdi-picker__size" data-size="lg" aria-pressed="false" title="Large (2em)">L</button>
              <button type="button" class="mdi-picker__size" data-size="xl" aria-pressed="false" title="Extra large (3em)">XL</button>
            </div>
          </div>
          <div class="mdi-picker__status"></div>
          <div class="mdi-picker__grid" role="listbox" aria-label="Icon grid"></div>
        </div>
      </div>`;
    document.body.appendChild(dialog);

    const overlay = dialog.querySelector(".w-dialog__overlay");
    const closeBtn = dialog.querySelector(".mdi-picker__close");
    const searchInput = dialog.querySelector(".mdi-picker__search");
    const sizeButtons = dialog.querySelectorAll(".mdi-picker__size");
    const grid = dialog.querySelector(".mdi-picker__grid");
    const status = dialog.querySelector(".mdi-picker__status");

    let selectedSize = "sm";
    let allIcons = null;
    let filtered = null;
    let page = 0;
    let searchTimer = null;
    let previouslyFocused = null;

    const show = () => {
      previouslyFocused = document.activeElement;
      dialog.removeAttribute("aria-hidden");
      document.documentElement.style.overflowY = "hidden";
      searchInput.focus();
    };

    const close = (value) => {
      dialog.setAttribute("aria-hidden", "true");
      document.documentElement.style.overflowY = "";
      if (previouslyFocused) previouslyFocused.focus();
      dialog.remove();
      resolve(value);
    };

    overlay.addEventListener("click", () => close(null));
    closeBtn.addEventListener("click", () => close(null));

    const onKeydown = (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        close(null);
      }
    };
    document.addEventListener("keydown", onKeydown);

    const setSize = (size) => {
      selectedSize = size;
      sizeButtons.forEach((btn) => {
        btn.setAttribute("aria-pressed", btn.dataset.size === size ? "true" : "false");
      });
    };
    sizeButtons.forEach((btn) => btn.addEventListener("click", () => setSize(btn.dataset.size)));

    const renderPage = () => {
      if (!filtered) return;
      const end = Math.min((page + 1) * PAGE_SIZE, filtered.length);
      const slice = filtered.slice(page * PAGE_SIZE, end);
      const fragment = slice.map(cellHtml).join("");
      grid.insertAdjacentHTML("beforeend", fragment);
      page++;
      const loaded = Math.min(page * PAGE_SIZE, filtered.length);
      status.textContent =
        `${filtered.length} icons` + (loaded < filtered.length ? ` — showing ${loaded}, scroll for more` : "");
    };

    const filterIcons = (query) => {
      if (!allIcons) return;
      const q = query.toLowerCase().trim();
      filtered = q ? allIcons.filter((i) => i.searchText.includes(q)) : allIcons;
      page = 0;
      grid.innerHTML = "";
      renderPage();
    };

    searchInput.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => filterIcons(searchInput.value), SEARCH_DEBOUNCE_MS);
    });

    grid.addEventListener("scroll", () => {
      if (grid.scrollTop + grid.clientHeight >= grid.scrollHeight - 50) {
        renderPage();
      }
    });

    grid.addEventListener("click", (e) => {
      const cell = e.target.closest(".mdi-picker__cell");
      if (!cell) return;
      document.removeEventListener("keydown", onKeydown);
      close({ name: cell.dataset.name, size: selectedSize });
    });

    grid.innerHTML = '<div class="mdi-picker__loading">Loading icons\u2026</div>';

    loadIcons()
      .then((icons) => {
        allIcons = icons;
        filtered = icons;
        grid.innerHTML = "";
        renderPage();
        show();
      })
      .catch(() => {
        grid.innerHTML =
          '<div class="mdi-picker__error">Could not load icons. Please close this dialog and try again.</div>';
        show();
      });
  });
}