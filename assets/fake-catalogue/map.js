import $ from 'jquery';

function displaySearchResults() {
  document.getElementById('search-results-container').style.display = 'block';

  const searchTerm = document.getElementById('searchterm').value;
  const resultBlockId = searchTerm == '' ? 'all-search-results' : 'search-results';
  const nonResultBlockId = searchTerm != '' ? 'all-search-results' : 'search-results';
  document.getElementById(resultBlockId).style.display = 'block';
  document.getElementById(nonResultBlockId).style.display = 'none';

  const activeFilterBlock = searchTerm == '' ? 'filter-box-all' : 'filter-box-search';
  const inactiveFilterBlock = searchTerm != '' ? 'filter-box-all' : 'filter-box-search';
  document.getElementById(activeFilterBlock).style.display = 'inline-block';
  document.getElementById(inactiveFilterBlock).style.display = 'none';
}

function hideSearchResults() {
  document.getElementById('search-results-container').style.display = 'none';
}

function showHideSearchForFocusChange() {
  // setTimeout is necessary to combine multiple events. When focus moves from somewhere in the
  // search are to somewhere else in the search area we get both a focusout and focusin.
  setTimeout(() => {
    const isFocused = $(document.activeElement).parents('#search-area').length;
    if (isFocused) {
      displaySearchResults();
    } else {
      hideSearchResults();
    }
  }, 0);
}

function hideSearchForFocusClickElsewhere(event) {
  const clickOutsideSearch = !$(event.target).parents('#search-area').length;
  if (clickOutsideSearch) hideSearchResults();
}

function showPointItemSearchResults(event) {
  const currentlyShown = $('#point-search-results-box').css('display') != 'none';
  if ((event.target.id == 'map-image' || event.target.id == 'aoi') && !currentlyShown) {
    $('#point-search-results-box').show();
    $('#point-search-results-box').css('left', event.pageX + 10 + 'px');

    // For some reason the images and accompanying text sometimes appear selected.
    getSelection().empty();
  } else {
    if (!$(event.target).parents('#point-search-results-box').length) {
      $('#point-search-results-box').hide();
      $('.point-dataset-search-results-box').hide();
    }
  }
}

function showPointItemDatasetSearchResults(event) {
  const target = $(event.target);
  const initialSearchBox = $('#point-search-results-box');
  const targetBox = target.parents('.point-search-result-box');
  const boxToShow =
    targetBox[0].id == 'point-search-result-s2'
      ? 'point-dataset-search-results-box-s2'
      : targetBox[0].id == 'point-search-result-ard'
        ? 'point-dataset-search-results-box-ard'
        : 'point-dataset-search-results-box-planet';
  const currentlyShown = $('#' + boxToShow).css('display') != 'none';
  if (target.parents('.point-search-result-box') && !currentlyShown) {
    $('.point-dataset-search-results-box').hide();
    $('#' + boxToShow).show();
    $('#' + boxToShow).css(
      'left',
      initialSearchBox.position().left + initialSearchBox.width() + 10 + 'px',
    );
  } else {
    if (!$(event.target).parents('.point-dataset-search-results-box').length) {
      $('.point-dataset-search-results-box').hide();
    }
  }
}

function copyURLButtonPress(event) {
  navigator.clipboard.writeText($(event.target).attr('data-stac-url'));
}

$(() => {
  $('#search-area').on('focusin', showHideSearchForFocusChange);
  $(document.body).on('click', hideSearchForFocusClickElsewhere);
  $('#map-image').on('click', showPointItemSearchResults);
  $('#search-form').on('submit', displaySearchResults);
  $('.point-search-copy-button').on('click', copyURLButtonPress);
  $('#point-search-results-box').on('click', showPointItemDatasetSearchResults);
});
