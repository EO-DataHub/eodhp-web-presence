import $ from 'jquery';

const runSearch = (input) => {
  $.get({
    url: '/support/search_items',
    data: { query: input },
  })
    .done((result) => {
      $('#supportTopicSearchResults').html(result);
    })
    .fail((error) => {
      console.log('Unable to search');
      alert('Error: ' + error.statusText);
    });
};

function filterItemsIndex() {
  const input = document.getElementById('searchBoxIndex').value;
  if (input === '') {
    document.getElementById('supportTopicSearchResults').innerHTML = '';
  } else {
    runSearch(input);
  }
}

function filterItemsArea() {
  const input = document.getElementById('searchBoxArea').value;
  runSearch(input);
}

$(() => {
  $('#searchBoxIndex').on('keyup', filterItemsIndex);
  $('#searchBoxArea').on('keyup', filterItemsArea);
});
