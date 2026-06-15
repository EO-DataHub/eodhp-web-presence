import $ from 'jquery';

function initHeroCarousel(root) {
  const $root = $(root);
  const $backgrounds = $root.find('.hero-carousel__bg');
  const $captions = $root.find('.hero-carousel__caption');
  const $dots = $root.find('.hero-carousel__dots');
  const interval = parseInt($root.attr('data-interval'), 10) || 8000;

  if ($backgrounds.length <= 1) {
    $root.find('.hero-carousel__controls').hide();
    return;
  }

  let index = 0;
  let timer = null;

  function show(i) {
    index = (i + $backgrounds.length) % $backgrounds.length;
    $backgrounds.removeClass('is-active').eq(index).addClass('is-active');
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

  $backgrounds.each(function (i) {
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
