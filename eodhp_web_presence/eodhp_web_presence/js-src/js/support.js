import $ from 'jquery'

const runSearch = async(input) => {
    const request = new XMLHttpRequest();
    await request.open('GET', '/support/search_items?query=' + encodeURIComponent(input), true);
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            document.getElementById('supportTopicSearchResults').innerHTML = request.responseText;
        }
    }
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
