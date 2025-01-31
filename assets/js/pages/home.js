import $ from 'jquery';

$(document).ready(function () {
  const $slides = $('.who-is-it-for__content__right .scroll-card');
  const $arrowLeft = $('#arrowLeft');
  const $arrowRight = $('#arrowRight');
  let currentSlide = 0;

  showSlide(currentSlide);

  $arrowLeft.on('click', function () {
    currentSlide = currentSlide <= 0 ? $slides.length - 1 : currentSlide - 1;
    showSlide(currentSlide, 'left');
  });

  $arrowRight.on('click', function () {
    currentSlide = currentSlide >= $slides.length - 1 ? 0 : currentSlide + 1;
    showSlide(currentSlide, 'right');
  });

  function showSlide(index, direction) {
    $slides.removeClass('active slide-in-left slide-in-right');

    const $newSlide = $slides.eq(index);
    $newSlide.addClass('active slide-in-' + (direction === 'right' ? 'right' : 'left'));
  }
});
