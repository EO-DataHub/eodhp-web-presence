function initTopicsFilter() {
  document.querySelectorAll('.faq-filters').forEach(function (bar) {
    var section = bar.nextElementSibling;
    if (!section || !section.classList.contains('faq-cards')) return;

    var buttons = bar.querySelectorAll('.faq-filter-btn');
    var allBtn = bar.querySelector('.faq-filter-btn[data-label=""]');

    function applyFilters() {
      var activeLabels = [];
      bar.querySelectorAll('.faq-filter-btn--active').forEach(function (b) {
        if (b.dataset.label) {
          activeLabels.push(b.dataset.label);
        }
      });

      section.querySelectorAll('.faq-card').forEach(function (card) {
        if (activeLabels.length === 0) {
          card.style.display = '';
        } else {
          var cardLabels = (card.dataset.labels || '').split(',');
          card.style.display = activeLabels.some(function (lbl) {
            return cardLabels.indexOf(lbl) !== -1;
          }) ? '' : 'none';
        }
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var label = btn.dataset.label;

        if (!label) {
          // "All" button: deactivate all label buttons
          buttons.forEach(function (b) {
            b.classList.remove('faq-filter-btn--active');
          });
          btn.classList.add('faq-filter-btn--active');
        } else {
          // Toggle this label button
          btn.classList.toggle('faq-filter-btn--active');
          // If any label is active, deactivate "All"
          if (btn.classList.contains('faq-filter-btn--active')) {
            if (allBtn) allBtn.classList.remove('faq-filter-btn--active');
          } else {
            // If no labels are active, reactivate "All"
            var anyActive = bar.querySelectorAll('.faq-filter-btn--active[data-label]').length > 0;
            if (!anyActive && allBtn) allBtn.classList.add('faq-filter-btn--active');
          }
        }

        applyFilters();
      });
    });
  });
}

document.addEventListener('DOMContentLoaded', initTopicsFilter);