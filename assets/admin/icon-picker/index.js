import '@mdi/font/css/materialdesignicons.min.css';
import './icon-picker.scss';
import { IconDecorator } from './decorator.js';
import { IconSource } from './source.js';

const register = () => {
  const draftail = window.draftail;
  if (!draftail || typeof draftail.registerPlugin !== 'function') {
    return false;
  }
  draftail.registerPlugin(
    {
      type: 'ICON',
      source: IconSource,
      decorator: IconDecorator,
    },
    'entityTypes',
  );
  return true;
};

if (!register()) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', register);
  } else {
    let attempts = 0;
    const t = setInterval(() => {
      if (register() || ++attempts > 20) clearInterval(t);
    }, 100);
  }
}
