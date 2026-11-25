// transactions.js - search and filter the list without loading the page again.

var searchBox = document.getElementById("search");
var rows = document.querySelectorAll(".transaction-row");
var filterButtons = document.querySelectorAll(".filter-button");
var countText = document.getElementById("count");
var noResults = document.getElementById("no-results");

var currentFilter = "all";


// Show the rows that fit the search text and the chosen filter
function updateList() {
  var searchText = searchBox.value.toLowerCase();
  var shown = 0;

  for (var i = 0; i < rows.length; i++) {
    var type = rows[i].getAttribute("data-type");
    var text = rows[i].getAttribute("data-search").toLowerCase();

    var typeFits = (currentFilter === "all" || currentFilter === type);
    var textFits = (text.indexOf(searchText) !== -1);

    if (typeFits && textFits) {
      rows[i].style.display = "flex";
      shown = shown + 1;
    } else {
      rows[i].style.display = "none";
    }
  }

  countText.textContent = "Showing " + shown + " of " + rows.length;

  if (shown === 0) {
    noResults.style.display = "block";
  } else {
    noResults.style.display = "none";
  }
}


// When the user types in the search box
searchBox.addEventListener("input", updateList);


// When the user clicks All, Income or Expenses
function chooseFilter(button) {
  currentFilter = button.getAttribute("data-filter");

  for (var i = 0; i < filterButtons.length; i++) {
    filterButtons[i].className = "button button-light button-small filter-button";
  }
  button.className = "button button-small filter-button";

  updateList();
}

for (var j = 0; j < filterButtons.length; j++) {
  filterButtons[j].addEventListener("click", function () {
    chooseFilter(this);
  });
}

updateList();
