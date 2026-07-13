// main.js — JavaScript for Care Circle
// Interactive behavior for the site.

// =====================================================
// 1. Shrinking header on scroll
// -----------------------------------------------------
// Grab the navbar, then listen for the page scrolling.
// Once the user has scrolled down a little, add the
// "scrolled" class (the CSS handles the actual shrinking).
// =====================================================
const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", function () {
    if (window.scrollY > 40) {
        navbar.classList.add("scrolled");     // past 40px down → shrink
    } else {
        navbar.classList.remove("scrolled");  // back at the top → full size
    }
});
