import "@mdi/font/css/materialdesignicons.min.css";
import "./icon-field.scss";
import { openIconModal } from "../icon-picker/modal.js";
import { isValidIconName } from "../icon-picker/icons.js";

const ICONFIELD_SELECTOR = '[data-contentpath="icon_name"]';

function renderPreview(preview, name) {
  preview.innerHTML = "";
  if (!name) return;
  const icon = document.createElement("span");
  icon.className = `mdi mdi-${name}`;
  icon.setAttribute("aria-hidden", "true");
  icon.setAttribute("data-mdi-icon", name);
  preview.appendChild(icon);
  const label = document.createElement("span");
  label.className = "icon-field__label";
  label.textContent = name;
  preview.appendChild(label);
}

function attachField(container) {
  if (container.dataset.iconPickerInit) return;
  container.dataset.iconPickerInit = "true";

  const input = container.querySelector("input[type=text]");
  if (!input) return;

  const wrapper = document.createElement("div");
  wrapper.className = "icon-field";

  const preview = document.createElement("span");
  preview.className = "icon-field__preview";
  renderPreview(preview, input.value);

  const pickBtn = document.createElement("button");
  pickBtn.type = "button";
  pickBtn.className = "icon-field__pick button button-small";
  pickBtn.textContent = "Pick icon";

  const clearBtn = document.createElement("button");
  clearBtn.type = "button";
  clearBtn.className = "icon-field__clear button button-secondary button-small";
  clearBtn.textContent = "Clear";

  const sizeName = input.name.replace(/icon_name$/, "icon_size");
  const sizeSelect =
    sizeName !== input.name
      ? document.querySelector(`select[name="${CSS.escape(sizeName)}"]`)
      : null;

  pickBtn.addEventListener("click", () => {
    openIconModal().then((choice) => {
      if (!choice || !isValidIconName(choice.name)) return;
      input.value = choice.name;
      renderPreview(preview, choice.name);
      input.dispatchEvent(new Event("change", { bubbles: true }));
      if (sizeSelect && choice.size) {
        const hasOption = Array.from(sizeSelect.options).some((o) => o.value === choice.size);
        if (hasOption) {
          sizeSelect.value = choice.size;
          sizeSelect.dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
    });
  });

  clearBtn.addEventListener("click", () => {
    input.value = "";
    renderPreview(preview, "");
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });

  const fieldInput = input.closest("[data-field-input]");
  if (fieldInput) {
    fieldInput.insertBefore(wrapper, input);
  } else {
    input.parentNode.insertBefore(wrapper, input);
  }
  wrapper.appendChild(input);
  wrapper.appendChild(preview);
  wrapper.appendChild(pickBtn);
  wrapper.appendChild(clearBtn);
  input.type = "hidden";
}

function scan(root) {
  (root || document).querySelectorAll(`${ICONFIELD_SELECTOR}:not([data-icon-picker-init])`).forEach(attachField);
}

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (node.nodeType !== Node.ELEMENT_NODE) continue;
      if (node.matches?.(ICONFIELD_SELECTOR) && !node.dataset.iconPickerInit) {
        attachField(node);
      }
      scan(node);
    }
  }
});

function start() {
  const editor = document.querySelector("[data-stream-field]") || document.body;
  observer.observe(editor, { childList: true, subtree: true });
  scan();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start);
} else {
  start();
}