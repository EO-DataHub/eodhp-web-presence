import $ from 'jquery'

const filterItemsIndex = async() => {
    const input = document.getElementById('searchBoxIndex').value;
    if (input === '') {
        document.getElementById('supportTopicSearchResults').innerHTML = '';
    }
    else {
        const request = new XMLHttpRequest();
        await request.open('GET', '/support/search_items?query=' + encodeURIComponent(input), true);
        request.onreadystatechange = function() {
            if (request.readyState == 4 && request.status == 200) {
                document.getElementById('supportTopicSearchResults').innerHTML = request.responseText;
            }
        }
        await request.send()
    }
}

const filterItemsArea = async() => {
    const input = document.getElementById('searchBoxArea').value;
    const request = new XMLHttpRequest();
    await request.open('GET', '/support/search_items?query=' + encodeURIComponent(input), true);
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            document.getElementById('supportTopicSearchResults').innerHTML = request.responseText;
        }
    }
    await request.send()
}

$(() => {
    $('#searchBoxIndex').on("keyup", filterItemsIndex)
    $('#searchBoxArea').on("keyup", filterItemsArea)
})
