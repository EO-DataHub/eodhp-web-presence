
import $ from 'jquery'

function displaySearchResults() {
    const searchTerm = document.getElementById('searchterm').value
    const resultBlockId = searchTerm == '' ? 'all-search-results' : 'search-results'
    const nonResultBlockId = searchTerm != '' ? 'all-search-results' : 'search-results'
    document.getElementById('search-results-container').style.display = 'block'
    document.getElementById(resultBlockId).style.display = 'block'
    document.getElementById(nonResultBlockId).style.display = 'none'
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

$(() => {
    document.getElementById('search-area').addEventListener("focusin", showHideSearchForFocusChange)
    document.body.addEventListener("click", hideSearchForFocusClickElsewhere)
    document.getElementById('search-form').addEventListener("submit", displaySearchResults)
})
