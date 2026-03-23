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

  setTimeout(function () {
    $('body').removeClass('no-transition');
  }, 1000);

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

  // Dropdown toggles — arrow click opens/closes the dropdown menu
  $('.dropdown__toggle').on('click', function (e) {
    const $toggle = $(this);
    const hasArrow = $toggle.find('.arrow').length > 0;

    if (hasArrow && !$(e.target).closest('.arrow').length) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();
    const $parent = $toggle.closest('.dropdown');
    const isOpen = $parent.hasClass('open');

    $('.dropdown').removeClass('open');

    if (!isOpen) {
      $parent.addClass('open');
    }
  });

  // On mobile: first tap opens dropdown, second tap follows the link
  $('.dropdown__toggle a').on('click', function (e) {
    if (window.innerWidth <= 1200) {
      const $parent = $(this).closest('.dropdown');
      if (!$parent.hasClass('open')) {
        e.preventDefault();
        $('.dropdown').removeClass('open');
        $parent.addClass('open');
      }
    }
  });

  // close dropdown if user clicks outside
  $(document).on('click', function (e) {
    if (!$(e.target).closest('.dropdown').length) {
      $('.dropdown').removeClass('open');
    }
  });
});
