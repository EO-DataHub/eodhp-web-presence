import $ from 'jquery';

// Carousel used by the homepage case study cards. One instance per
// [data-carousel] element; slide count per view is derived from the
// rendered slide width.
function initCarousel(root) {
  const $root = $(root);
  const $viewport = $root.find('.case-carousel__viewport').first();
  const $track = $root.find('.case-carousel__track').first();
  const $slides = $track.children('.case-carousel__slide');
  const $dots = $root.find('.case-carousel__dots').first();
  const autoplayMs = parseInt($root.attr('data-autoplay'), 10) || 0;

  let index = 0;
  let timer = null;
  let touchStartX = null;

  if ($slides.length <= 1) {
    $root.find('.case-carousel__controls').hide();
    return;
  }

  function slideStep() {
    return $slides.first().outerWidth(true) || $viewport.innerWidth();
  }

  function visibleCount() {
    return Math.max(1, Math.round($viewport.innerWidth() / slideStep()));
  }

  function maxIndex() {
    return Math.max(0, $slides.length - visibleCount());
  }

  function buildDots() {
    $dots.empty();
    for (let i = 0; i <= maxIndex(); i += 1) {
      $('<button>', {
        type: 'button',
        class: 'case-carousel__dot',
        'aria-label': `Go to slide ${i + 1}`,
      }).appendTo($dots);
    }
  }

  function update() {
    $track.css('transform', `translateX(${-index * slideStep()}px)`);

    $dots.children().each(function (i) {
      $(this).toggleClass('is-active', i === index);
      this.setAttribute('aria-current', i === index ? 'true' : 'false');
    });

    const visibleFrom = index;
    const visibleTo = index + visibleCount();
    $slides.each(function (i) {
      const hidden = i < visibleFrom || i >= visibleTo;
      $(this).attr('aria-hidden', hidden ? 'true' : 'false');
      $(this).find('a, button').attr('tabindex', hidden ? -1 : 0);
    });
  }

  function goTo(i) {
    const max = maxIndex();
    if (i < 0) {
      index = max;
    } else if (i > max) {
      index = 0;
    } else {
      index = i;
    }
    update();
  }

  function stopAutoplay() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function startAutoplay() {
    if (!autoplayMs) return;
    stopAutoplay();
    timer = setInterval(() => goTo(index + 1), autoplayMs);
  }

  $root.find('.case-carousel__arrow--prev').on('click', () => {
    goTo(index - 1);
    startAutoplay();
  });
  $root.find('.case-carousel__arrow--next').on('click', () => {
    goTo(index + 1);
    startAutoplay();
  });
  $dots.on('click', '.case-carousel__dot', function () {
    goTo($(this).index());
    startAutoplay();
  });

  $root.on('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      goTo(index - 1);
      startAutoplay();
    } else if (event.key === 'ArrowRight') {
      goTo(index + 1);
      startAutoplay();
    }
  });

  $viewport.on('touchstart', (event) => {
    touchStartX = event.originalEvent.changedTouches[0].clientX;
  });
  $viewport.on('touchend', (event) => {
    if (touchStartX === null) return;
    const delta = event.originalEvent.changedTouches[0].clientX - touchStartX;
    touchStartX = null;
    if (Math.abs(delta) > 40) {
      goTo(delta < 0 ? index + 1 : index - 1);
      startAutoplay();
    }
  });

  $root.on('mouseenter focusin', stopAutoplay);
  $root.on('mouseleave focusout', startAutoplay);

  let resizeTimer = null;
  $(window).on('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if ($dots.children().length !== maxIndex() + 1) {
        buildDots();
      }
      goTo(Math.min(index, maxIndex()));
    }, 150);
  });

  buildDots();
  update();
  startAutoplay();
}

$(document).ready(() => {
  $('[data-carousel]').each(function () {
    initCarousel(this);
  });
});
