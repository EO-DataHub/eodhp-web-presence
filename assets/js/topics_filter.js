function initTopicsFilter() {
  document.querySelectorAll('.faq-filters').forEach((bar) => {
    var section = bar.nextElementSibling;
    if (!section?.classList.contains('faq-cards')) return;

    var buttons = bar.querySelectorAll('.faq-filter-btn');
    var allBtn = bar.querySelector('.faq-filter-btn[data-label=""]');

    function applyFilters() {
      var activeLabels = [];
      bar.querySelectorAll('.faq-filter-btn--active').forEach((b) => {
        if (b.dataset.label) {
          activeLabels.push(b.dataset.label);
        }
      });

      section.querySelectorAll('.faq-card').forEach((card) => {
        if (activeLabels.length === 0) {
          card.style.display = '';
        } else {
          const cardLabels = (card.dataset.labels || '').split(',');
          card.style.display = activeLabels.some((lbl) => cardLabels.indexOf(lbl) !== -1)
            ? ''
            : 'none';
        }
      });
    }

    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        var label = btn.dataset.label;

        if (!label) {
          // "All" button: deactivate all label buttons
          buttons.forEach((b) => {
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
            const anyActive =
              bar.querySelectorAll('.faq-filter-btn--active[data-label]').length > 0;
            if (!anyActive && allBtn) allBtn.classList.add('faq-filter-btn--active');
          }
        }

        applyFilters();
      });
    });
  });
}

document.addEventListener('DOMContentLoaded', initTopicsFilter);
