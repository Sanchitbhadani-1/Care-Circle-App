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

// =====================================================
// 3. Scroll reveal
// -----------------------------------------------------
// Fade + slide elements in as they scroll into view,
// using an IntersectionObserver — the browser notifies
// us the moment a watched element enters the screen.
// =====================================================

// The elements we want to animate in.
const revealItems = document.querySelectorAll(
    ".feature-card, .step, .section-title, .trust-content"
);

// Give each one the hidden starting state. We do this in JS (not the
// HTML) so that if JavaScript is ever off, nothing hides — the page
// just shows normally.
revealItems.forEach(function (el) {
    el.classList.add("reveal");
});

// Create the watcher. Its function runs whenever a watched element
// crosses into view.
const revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");   // slide it in
            revealObserver.unobserve(entry.target);  // reveal once, then stop watching
        }
    });
}, { threshold: 0.15 });   // fire when ~15% of the element is on screen

// Tell the watcher which elements to keep an eye on.
revealItems.forEach(function (el) {
    revealObserver.observe(el);
});
