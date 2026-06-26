document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.breadcrumbs__ellipsis-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      var nav = btn.closest('.breadcrumbs');
      if (nav) {
        nav.classList.add('breadcrumbs--expanded');
      }
    });
  });
});
