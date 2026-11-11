import $ from 'jquery';

var STORAGE_KEY = 'eodhp_banner_dismissed';

// localStorage throws when the browser blocks site data.
function readDismissed() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function saveDismissed(key) {
  try {
    localStorage.setItem(STORAGE_KEY, key);
  } catch {
    // Dismissal lasts for this page view only.
  }
}

$(document).ready(() => {
  var $banner = $('.notification-banner');
  if (!$banner.length) {
    return;
  }

  var dismissKey = $banner.data('dismiss-key');
  if (!dismissKey) {
    return;
  }

  // Hide immediately if this banner was previously dismissed.
  if (readDismissed() === dismissKey) {
    $banner.remove();
    return;
  }

  $banner.on('click', '.notification-banner__dismiss', () => {
    saveDismissed(dismissKey);
    $banner.remove();
  });

  var $message = $banner.find('.notification-banner__message');
  var $toggle = $banner.find('.notification-banner__toggle');

  function updateTruncated() {
    if ($banner.hasClass('notification-banner--expanded')) {
      return;
    }
    var el = $message[0];
    $banner.toggleClass('notification-banner--truncated', el.scrollHeight > el.clientHeight + 1);
  }

  function setExpanded(expanded) {
    $banner.toggleClass('notification-banner--expanded', expanded);
    $toggle.attr('aria-expanded', expanded).text(expanded ? 'Less' : 'More');
    updateTruncated();
  }

  $toggle.on('click', () => {
    setExpanded(!$banner.hasClass('notification-banner--expanded'));
  });

  // A link inside the clipped part of the message can still take focus.
  $message.on('focusin', () => {
    if ($banner.hasClass('notification-banner--truncated')) {
      setExpanded(true);
    }
  });

  updateTruncated();
  $(window).on('resize', updateTruncated);
  if (document.fonts) {
    document.fonts.ready.then(updateTruncated);
  }
});
