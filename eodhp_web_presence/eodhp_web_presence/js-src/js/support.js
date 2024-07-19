import $ from 'jquery'

const runSearch = async(input) => {
    const request = new XMLHttpRequest();
    $.get({'url': '/support/search_items', 'data': {'query': input}}).done((result) => {
        $('#supportTopicSearchResults').html(result);
    })
    await request.send()
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
    runSearch(input);
}

$(() => {
    $('#searchBoxIndex').on("keyup", filterItemsIndex)
    $('#searchBoxArea').on("keyup", filterItemsArea)
})
