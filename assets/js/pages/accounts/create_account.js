import $ from 'jquery';

$(document).ready(function () {
  $('#open-create-account').on('click', function () {
    $('#create-account-modal').fadeIn();
  });

  $('.close-button').on('click', function () {
    $('#create-account-modal').fadeOut();
  });

  $(window).on('click', function (e) {
    if ($(e.target).is('#create-account-modal')) {
      $('#create-account-modal').fadeOut();
    }
  });

  // On Submit
  $('#create-account-form').on('submit', function (e) {
    e.preventDefault();

    const accountOwner = $('#account-owner').val().trim();
    const accountName = $('#account-name').val().trim();
    const billingAddress = $('#billing-address').val().trim();
    const organizationName = $('#organization-name').val().trim();
    const accountOpeningReason = $('#account-opening-reason').val().trim();
    const agreeTerms = $('#agree-terms').is(':checked');

    // Validate
    if (
      !accountOwner ||
      !accountName ||
      !billingAddress ||
      !organizationName ||
      !accountOpeningReason ||
      !agreeTerms
    ) {
      $('#create-account-message').text(
        'Please complete all required fields and agree to the terms.'
      );
      return;
    }

    const payload = {
      accountOwner: accountOwner,
      name: accountName,
      billingAddress: billingAddress,
      organizationName: organizationName,
      accountOpeningReason: accountOpeningReason,
    };

    // Send request
    $.ajax({
      url: '/api/accounts',
      method: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify(payload),
      success: function (data) {
        $('#create-account-message')
          .css('color', '#4c72ba')
          .text('Account created successfully! Please wait while we refresh the list...');
        setTimeout(function () {
          location.reload();
        }, 1500);
      },
      error: function (xhr, status, error) {
        $('#create-account-message')
          .css('color', '#d9534f')
          .text('Failed to create account. Please try again.');
      },
    });
  });
});