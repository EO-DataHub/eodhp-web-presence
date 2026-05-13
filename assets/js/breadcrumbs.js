document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.breadcrumbs__ellipsis-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var nav = btn.closest('.breadcrumbs');
      if (nav) {
        nav.classList.add('breadcrumbs--expanded');
      }
    });
  });
});