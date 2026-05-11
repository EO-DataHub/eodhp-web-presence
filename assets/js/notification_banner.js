import $ from 'jquery';

$(document).ready(function () {
  var $banner = $('.notification-banner');
  if (!$banner.length) {
    return;
  }

  var dismissKey = $banner.data('dismiss-key');
  if (!dismissKey) {
    return;
  }

  // Hide immediately if this banner was previously dismissed.
  if (localStorage.getItem('eodhp_banner_dismissed') === dismissKey) {
    $banner.remove();
    return;
  }

  $banner.on('click', '.notification-banner__dismiss', function () {
    localStorage.setItem('eodhp_banner_dismissed', dismissKey);
    $banner.remove();
  });
});
