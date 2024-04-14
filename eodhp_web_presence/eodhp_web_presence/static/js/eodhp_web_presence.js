var mobileMenuButton = document.querySelector("#mobile-menu-btn");
var mobileMenu = document.querySelector(".mobile-menu");
mobileMenuButton.addEventListener("click", () => {
    console.log('"""""""""""""""""');
    if (mobileMenu.style.display === "none") {
        console.log('zzzzzzzzzzzzzzzzzzzz');
        mobileMenu.style.display = "flex";
        mobileMenuButton.style.backgroundColor = "red";
        mobileMenuButton.style.width = "100vw";
//        mobileMenuBtnSrc = "/static/img/menu/right_arrow.svg"
    }
    else {
        console.log("xxxxxxxxxxxxxxxxxx");
        mobileMenu.style.display = "none";
//        mobileMenuBtnSrc = "/static/img/menu/right_arrow.svg"

    }
});

var hideMenu = document.querySelector("hide_menu");menu_minimise_button.addEventListener("click", () => {
    var menu_image = document.getElementById("hide_menu");
    var menu = document.getElementById("menu");
    var main_content = document.getElementById("main-content");
    if (menu_image.src.split('/').at(-1) === "left_arrow.svg") {
        menu_image.src = "/static/img/menu/right_arrow.svg"
        var divsToHide = document.getElementsByClassName("menu_text");
        for(var i = 0; i < divsToHide.length; i++){
            console.log(divsToHide[i].style.display);
            divsToHide[i].style.display = "none";
        }
        menu.style.width = "100px";
        main_content.style.width = "calc(100% - 100px)";
    }
    else {
        menu_image.src = "/static/img/menu/left_arrow.svg"
        var divsToUnhide = document.getElementsByClassName("menu_text");
        for(var i = 0; i < divsToUnhide.length; i++){
            divsToUnhide[i].style.display = "inline";
        }
        menu.style.width = "270px";
        main_content.style.width = "calc(100% - 270px)";
    }
});


var minimiseMenu = document.getElementById("minimise_menu");
var menuMinimiseButton = document.getElementById("menu_minimise_button");
var sectionsToHide = [...document.getElementsByClassName("menu_section"), ...document.getElementsByClassName("menu_section_bottom"), ...document.getElementsByClassName("menu_section_spacer")];
var sectionsToShrink = [...document.getElementsByClassName("menu_items"), ...document.getElementsByClassName("horizontal_spacer_5_l"), ...document.getElementsByClassName("horizontal_spacer_5_r")]
minimiseMenu.onclick = function() {
    maximiseMenu = document.getElementById("menu_section_minimised");
    var style = window.getComputedStyle(maximiseMenu);
    var display = style.getPropertyValue('display');

    menuMinimiseButton.style.marginTop = "10px";
    maximiseMenu.style.display = "block";
    for(var i = 0; i < sectionsToHide.length; i++){
        sectionsToHide[i].style.display = "none";
    }
    for(var i = 0; i < sectionsToShrink.length; i++){
        sectionsToShrink[i].style.height = "60px";
    }
};
var maximiseMenu = document.getElementById("maximise_menu");
maximise_menu.onclick = function() {
    maximiseMenu = document.getElementById("menu_section_minimised");
    menuMinimiseButton.style.marginTop = "100px";
    maximiseMenu.style.display = "none"
    var style = window.getComputedStyle(maximiseMenu);
    var display = style.getPropertyValue('display');
    for(var i = 0; i < sectionsToHide.length; i++){
        sectionsToHide[i].style.display = "block";
    }
    for(var i = 0; i < sectionsToShrink.length; i++){
        sectionsToShrink[i].style.height = "100vh";
    }
};