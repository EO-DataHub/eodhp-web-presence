import $ from 'jquery';

$(document).ready(() => {
  // Theme toggle
  $('#dark-theme-toggle').on('click', () => {
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

  setTimeout(() => {
    $('body').removeClass('no-transition');
  }, 1000);

  // if on the home page, add transparent class to the menu
  if (window.location.pathname === '/') {
    const $menu = $('.menu');
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
  $('#menuToggle').on('click', () => {
    $('#mainMenu').toggleClass('open');
  });

  const closeSubMenus = ($subs) => {
    $subs.removeClass('open').find('> .dropdown__sub-toggle').attr('aria-expanded', 'false');
  };

  const closeDropdowns = ($dropdowns) => {
    $dropdowns.removeClass('open').find('> .dropdown__toggle').attr('aria-expanded', 'false');
    closeSubMenus($dropdowns.find('.dropdown__sub'));
  };

  const openDropdown = ($dropdown) => {
    $dropdown.addClass('open').find('> .dropdown__toggle').attr('aria-expanded', 'true');
  };

  // Dropdown toggles — the whole parent control opens/closes the child menu.
  $('.dropdown__toggle').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $parent = $(this).closest('.dropdown');
    const isOpen = $parent.hasClass('open');

    closeDropdowns($('.dropdown').not($parent));

    if (isOpen) {
      closeDropdowns($parent);
    } else {
      openDropdown($parent);
    }
  });

  // Account menu sub-items (username, Workspace settings, My data) open on
  // hover via CSS on desktop; this click handler covers touch/keyboard use.
  $('.dropdown__sub-toggle').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $sub = $(this).closest('.dropdown__sub');
    const isOpen = $sub.hasClass('open');

    closeSubMenus($sub.siblings('.dropdown__sub'));

    if (isOpen) {
      closeSubMenus($sub);
    } else {
      $sub.addClass('open');
      $(this).attr('aria-expanded', 'true');
    }
  });

  $('.dropdown').on('keydown', function (e) {
    if (e.key === 'Escape') {
      closeDropdowns($(this));
      $(this).find('> .dropdown__toggle').trigger('focus');
    }
  });

  // close dropdown if user clicks outside
  $(document).on('click', (e) => {
    if (!$(e.target).closest('.dropdown').length) {
      closeDropdowns($('.dropdown'));
    }
  });
});
