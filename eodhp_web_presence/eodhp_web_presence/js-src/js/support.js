import $ from 'jquery'

const runSearch = async(input) => {
    try {
        await $.get({'url': '/support/search_items', 'data': {'query': input}}).done((result) => {
            $('#supportTopicSearchResults').html(result);
        })
    }
    catch(err) {
        console.log("Unable to search");
        alert(err);
    }
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
