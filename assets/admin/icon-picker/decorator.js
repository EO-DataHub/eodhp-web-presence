import { DEFAULT_SIZE, isValidIconName, isValidSize } from './icons.js';

export const IconDecorator = ({ contentState, entityKey, children }) => {
  const data = contentState.getEntity(entityKey).getData();
  const name = isValidIconName(data.name) ? data.name : '';
  const size = isValidSize(data.size) ? data.size : DEFAULT_SIZE;
  return window.React.createElement(
    'span',
    {
      className: name ? `mdi mdi-${name}` : 'mdi',
      'aria-hidden': 'true',
      'data-mdi-icon': name,
      'data-mdi-size': size,
      contentEditable: false,
    },
    children,
  );
};
