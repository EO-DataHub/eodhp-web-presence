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

  const createAccountsContainer = (data) => {
    const container = $('#accounts-container');
    container.empty();
    if (data.length === 0) {
      container.append('<p class="placeholder">No accounts available.</p>');
    } else {
      data.forEach(function (account) {
        container.append(createAccountCard(account));
      });
    }
  };

  if (window.location.hostname === 'localhost') {
    const placeholderAccountNum = 4;
    const account = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      createdAt: '2025-01-01T12:00:00.000Z',
      name: 'Sample Account',
      accountOwner: 'john-doe',
      billingAddress: '123 Fake Street, Faketown, FK1 2AB',
      organizationName: 'Fake Organization',
      accountOpeningReason: 'Testing',
      workspaces: [
        {
          id: '987e6543-b21a-34c5-d678-123456789abc',
          name: 'john-doe-workspace',
          account: '123e4567-e89b-12d3-a456-426614174000',
          member_group: 'john-doe-group',
          status: 'Active',
          stores: [
            {
              object: [
                {
                  store_id: 'abc12345-6789-0123-4567-89abcdef0123',
                  name: 'john-doe-store',
                  bucket: 'workspaces-fake-bucket',
                  prefix: 'john-doe/',
                  host: 'fake-bucket.s3-accesspoint.fake-region.amazonaws.com',
                  env_var: 'S3_BUCKET_WORKSPACE',
                  access_point_arn:
                    'arn:aws:s3:fake-region:123456789012:accesspoint/fake-access-point',
                  access_url: 'https://john-doe.fake-workspaces.org/files/workspaces-fake-bucket/',
                },
              ],
              block: [
                {
                  store_id: 'def67890-1234-5678-90ab-cdef12345678',
                  name: 'john-doe-block',
                  access_point_id: 'fsap-0123456789abcdef0',
                  mount_point: '/workspaces/john-doe',
                },
              ],
            },
          ],
          last_updated: '2025-01-02T12:00:00.000Z',
        },
      ],
    };

    let accounts = [];
    for (let i = 0; i < placeholderAccountNum; i++) {
      accounts.push(account);
    }

    createAccountsContainer(accounts);
  } else {
    $.ajax({
      url: '/api/accounts',
      method: 'GET',
      dataType: 'json',
      success: function (data) {
        createAccountsContainer(data);
      },

      error: function (xhr, status, error) {
        console.error('Error fetching accounts:', error);

        $('#accounts-container').html(
          '<p class="error">Failed to load accounts. Please try again later.</p>',
        );
      },
    });
  }
});
