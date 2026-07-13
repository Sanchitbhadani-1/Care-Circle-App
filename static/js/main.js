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

// =====================================================
// 2. Back-to-top button
// -----------------------------------------------------
// Reveal the button after scrolling down a bit, and
// smoothly glide back to the top when it's clicked.
// =====================================================
const backToTop = document.querySelector("#back-to-top");

// Show/hide it based on how far down the page we are.
window.addEventListener("scroll", function () {
    if (window.scrollY > 300) {
        backToTop.classList.add("show");
    } else {
        backToTop.classList.remove("show");
    }
});

// When clicked, scroll the window back to the very top.
backToTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
});
