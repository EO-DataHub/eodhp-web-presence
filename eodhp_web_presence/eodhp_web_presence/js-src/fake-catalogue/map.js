import $ from 'jquery'

function displaySearchResults() {
    document.getElementById('search-results-container').style.display = 'block'

    const searchTerm = document.getElementById('searchterm').value
    const resultBlockId = searchTerm == '' ? 'all-search-results' : 'search-results'
    const nonResultBlockId = searchTerm != '' ? 'all-search-results' : 'search-results'
    document.getElementById(resultBlockId).style.display = 'block'
    document.getElementById(nonResultBlockId).style.display = 'none'

    const activeFilterBlock = searchTerm == '' ? 'filter-box-all' : 'filter-box-search'
    const inactiveFilterBlock = searchTerm != '' ? 'filter-box-all' : 'filter-box-search'
    document.getElementById(activeFilterBlock).style.display = 'inline-block'
    document.getElementById(inactiveFilterBlock).style.display = 'none'

}

function hideSearchResults() {
    document.getElementById('search-results-container').style.display = 'none'
}

function showHideSearchForFocusChange() {
    // setTimeout is necessary to combine multiple events. When focus moves from somewhere in the
    // search are to somewhere else in the search area we get both a focusout and focusin.
    setTimeout(() => {
        const isFocused = $(document.activeElement).parents('#search-area').length
        if (isFocused) {
            displaySearchResults()
        } else {
            hideSearchResults()
        }
    }, 0)
}

function hideSearchForFocusClickElsewhere(event) {
    const clickOutsideSearch = !$(event.target).parents('#search-area').length
    if (clickOutsideSearch) hideSearchResults()
}

function showPointItemSearchResults(event) {
    // console.debug(event)
    const currentlyShown = $('#point-search-results-box').css('display') != 'none'
    if (event.target.id == 'map-image' && !currentlyShown) {
        $('#point-search-results-box').show()
        $('#point-search-results-box').css('left', (event.x + 10) + 'px')
    } else {
        if (!$(event.target).parents('#point-search-results-box').length) $('#point-search-results-box').hide()
    }
}

$(() => {
    document.getElementById('search-area').addEventListener("focusin", showHideSearchForFocusChange)
    document.body.addEventListener("click", hideSearchForFocusClickElsewhere)
    document.getElementById("map-image").addEventListener("click", showPointItemSearchResults)
    document.getElementById('search-form').addEventListener("submit", displaySearchResults)
})
