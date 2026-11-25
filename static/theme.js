// theme.js - remembers which theme the user picked.

// Get the saved theme (or "light" if nothing is saved yet)
var saved = localStorage.getItem("theme") || "light";
document.body.className = saved;

// The theme picker only exists in the menu (not on the login page)
var themeSelect = document.getElementById("theme");

if (themeSelect) {
  themeSelect.value = saved;

  // When the user picks a new theme, change it and save it
  themeSelect.addEventListener("change", function () {
    document.body.className = themeSelect.value;
    localStorage.setItem("theme", themeSelect.value);
  });
}
