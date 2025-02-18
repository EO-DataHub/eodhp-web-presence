import $ from 'jquery';

$(document).ready(function () {
  function createAccountCard(account) {
    let workspacesHTML = '';

    if (account.workspaces && account.workspaces.length > 0) {
      workspacesHTML = '<ul>';

      account.workspaces.forEach(function (ws) {
        workspacesHTML += `<li>${ws.name}</li>`;
      });

      workspacesHTML += '</ul>';
    } else {
      workspacesHTML = '<p class="placeholder">No workspaces found.</p>';
    }

    return `
      <div class="account-card">
        <div class="account-card__header">
          <h2>${account.name}</h2>
        </div>
        <div class="account-card__info">
          <h3>Contact</h3>
          <p><strong>Account Owner:</strong> ${account.accountOwner}</p>
        </div>
        <div class="account-card__workspaces">
          <h3>Workspaces</h3>
          ${workspacesHTML}
        </div>
      </div>
    `;
  }

  $.ajax({
    url: '/api/accounts',
    method: 'GET',
    dataType: 'json',
    success: function (data) {
      const container = $('#accounts-container');
      container.empty();
      if (data.length === 0) {
        container.append('<p class="placeholder">No accounts available.</p>');
      } else {
        data.forEach(function (account) {
          container.append(createAccountCard(account));
        });
      }
    },

    error: function (xhr, status, error) {
      console.error('Error fetching accounts:', error);

      $('#accounts-container').html(
        '<p class="error">Failed to load accounts. Please try again later.</p>',
      );
    },
  });
});
