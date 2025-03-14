import $ from 'jquery';

import { PLACEHOLDER_WORKSPACE } from '../placeholders/workspaces';

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

  const parseWorkspacesAndUpdateMenu = (workspaces) => {
    const notebookDropdown = $('#notebook-dropdown');
    if (workspaces && workspaces.length > 0) {
      notebookDropdown.html('');
      workspaces.forEach((workspace) => {
        const subdomain = window.location.hostname.split('.')[0];
        const workspaceLink = `<a href="https://${workspace.name}.${subdomain}.eodatahub-workspaces.org.uk/notebooks" class="dropdown__item">${workspace.name}</a>`;
        notebookDropdown.append(workspaceLink);
      });
    }
  };

  // Collect available user workspaces
  if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
    const numWorkspaces = 3;
    const PLACEHOLDER_WORKSPACES = Array.from(
      { length: numWorkspaces },
      () => PLACEHOLDER_WORKSPACE[0],
    );
    parseWorkspacesAndUpdateMenu(PLACEHOLDER_WORKSPACES);
  } else {
    $.ajax({
      url: '/api/workspaces',
      method: 'GET',
      dataType: 'json',
      success: function (response) {
        const workspaces = response;
        parseWorkspacesAndUpdateMenu(workspaces);
      },
      error: function (error) {
        console.error(error);
      },
    });
  }
});
