// budget.js - shows what the budget means while the user types.

var limitBox = document.getElementById("limit");
var preview = document.getElementById("preview");


// Turns 12000 into "12 000 kr"
function formatMoney(number) {
  var text = String(Math.round(number));
  var result = "";
  var count = 0;

  for (var i = text.length - 1; i >= 0; i--) {
    result = text.charAt(i) + result;
    count = count + 1;

    if (count % 3 === 0 && i > 0) {
      result = " " + result;
    }
  }

  return result + " kr";
}


function updatePreview() {
  var limit = Number(limitBox.value);

  if (limit <= 0) {
    preview.textContent = "";
    return;
  }

  var warningAt = limit * 0.8;
  var perDay = limit / 30;

  preview.textContent = "That is about " + formatMoney(perDay) + " per day. "
    + "You get a warning when you reach " + formatMoney(warningAt) + ".";
}

limitBox.addEventListener("input", updatePreview);
updatePreview();
