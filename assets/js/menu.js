import $ from 'jquery';

$(document).ready(function () {
  // Theme toggle
  $('#dark-theme-toggle').on('click', function () {
    $('body').toggleClass('light-theme dark-theme');

    // Update local storage
    if ($('body').hasClass('dark-theme')) {
      localStorage.setItem('theme', 'dark');
    } else {
      localStorage.setItem('theme', 'light');
    }
  });

  const theme = localStorage.getItem('theme');
  if (theme === 'dark') {
    $('body').removeClass('light-theme').addClass('dark-theme');
  } else {
    $('body').removeClass('dark-theme').addClass('light-theme');
  }

  // if on the home page, add transparent class to the menu
  if (window.location.pathname === '/') {
    let $menu = $('.menu');
    $menu.addClass('transparent top dark-theme');

    $(window).on('scroll', function () {
      if ($(this).scrollTop() > 0) {
        $menu.addClass('scrolled').removeClass('top dark-theme transparent');
      } else {
        $menu.removeClass('scrolled').addClass('top dark-theme transparent');
      }
    });
  }

  // Mobile hamburger toggle
  $('#menuToggle').on('click', function () {
    $('#mainMenu').toggleClass('open');
  });

  // Dropdown toggles on small screens
  $('.dropdown__toggle').on('click', function (e) {
    e.stopPropagation();
    const $parent = $(this).closest('.dropdown');
    const isOpen = $parent.hasClass('open');

    $('.dropdown').removeClass('open');

    if (!isOpen) {
      $parent.addClass('open');
    }
  });

  // close dropdown if user clicks outside
  $(document).on('click', function (e) {
    if (!$(e.target).closest('.dropdown').length) {
      $('.dropdown').removeClass('open');
    }
  });
});
