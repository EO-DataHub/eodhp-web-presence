import $ from 'jquery'

const runSearch = (input, areaSlug) => {
    $.get({
        url: '/support/search_items',
        data: { query: input, area: areaSlug }
    }).done((result) => {
        $('#supportTopicSearchResults').html(result);
    }).fail((error) => {
        console.log("Unable to search");
        alert("Error: " + error.statusText);
    });
}

function getAreaSlug() {
    const pathArray = window.location.pathname.split('/').filter(Boolean);
    return pathArray.length > 1 ? pathArray[1] : null;
}

function filterItemsIndex() {
    const input = document.getElementById('searchBoxIndex').value;
    if (input === '') {
        document.getElementById('supportTopicSearchResults').innerHTML = '';
    }
    else {
        runSearch(input);
    }
}

function filterItemsArea() {
    const input = document.getElementById('searchBoxArea').value;
    const areaSlug = getAreaSlug();
    console.log(areaSlug);
    runSearch(input, areaSlug);
}

$(() => {
    $('#searchBoxIndex').on("keyup", filterItemsIndex)
    $('#searchBoxArea').on("keyup", filterItemsArea)
})
