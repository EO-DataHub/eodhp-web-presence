import $ from 'jquery';

function initHeroCarousel(root) {
  const $root = $(root);
  const $backgrounds = $root.find('.hero-carousel__bg');
  const $captions = $root.find('.hero-carousel__caption');
  const $dots = $root.find('.hero-carousel__dots');
  const interval = parseInt($root.attr('data-interval'), 10) || 8000;
  const fadeCleanupMs = 1500;
  const leavingTimers = new WeakMap();

  if ($backgrounds.length <= 1) {
    $root.find('.hero-carousel__controls').hide();
    return;
  }

  let index = 0;
  let timer = null;

  function clearLeavingState(background) {
    const leaveTimer = leavingTimers.get(background);
    if (leaveTimer) {
      clearTimeout(leaveTimer);
      leavingTimers.delete(background);
    }

    $(background).off('transitionend.heroCarouselLeave');
    background.classList.remove('is-leaving');
    background.style.transform = '';
  }

  function cleanupAfterFade(background) {
    const finish = () => clearLeavingState(background);

    $(background)
      .off('transitionend.heroCarouselLeave')
      .on('transitionend.heroCarouselLeave', (event) => {
        const { propertyName } = event.originalEvent;
        if (propertyName && propertyName !== 'opacity') {
          return;
        }
        finish();
      });

    leavingTimers.set(background, setTimeout(finish, fadeCleanupMs));
  }

  function freezeAndFadeBackground(background) {
    // Freeze the animated zoom before removing is-active, otherwise the
    // background falls back to its final scale while it fades out.
    const currentTransform = window.getComputedStyle(background).transform || 'none';
    background.style.transform = currentTransform;
    background.classList.remove('is-active');
    background.classList.add('is-leaving');
    cleanupAfterFade(background);
  }

  function show(i) {
    const nextIndex = (i + $backgrounds.length) % $backgrounds.length;
    if (nextIndex === index) return;

    const currentBackground = $backgrounds.eq(index)[0];
    const nextBackground = $backgrounds.eq(nextIndex)[0];

    if (nextBackground) {
      clearLeavingState(nextBackground);
    }
    if (currentBackground) {
      freezeAndFadeBackground(currentBackground);
    }

    index = nextIndex;
    $backgrounds.not(nextBackground).removeClass('is-active');
    if (nextBackground) {
      nextBackground.classList.add('is-active');
    }
    $captions.removeClass('is-active').eq(index).addClass('is-active');
    $dots.children().each(function (j) {
      $(this).toggleClass('is-active', j === index);
      this.setAttribute('aria-current', j === index ? 'true' : 'false');
    });
  }

  function stop() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function start() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    stop();
    timer = setInterval(() => show(index + 1), interval);
  }

  $backgrounds.each((i) => {
    $('<button>', {
      type: 'button',
      class: 'hero-carousel__dot',
      'aria-label': `Show background image ${i + 1}`,
    }).appendTo($dots);
  });
  $dots.children().first().addClass('is-active').attr('aria-current', 'true');

  $dots.on('click', '.hero-carousel__dot', function () {
    show($(this).index());
    start();
  });

  $root.find('.hero-carousel__arrow--prev').on('click', () => {
    show(index - 1);
    start();
  });
  $root.find('.hero-carousel__arrow--next').on('click', () => {
    show(index + 1);
    start();
  });

  start();
}

$(document).ready(() => {
  $('[data-hero-carousel]').each(function () {
    initHeroCarousel(this);
  });
});
