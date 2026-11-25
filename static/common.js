// common.js - small things that every page uses.


// ---------- Messages hide by themselves after 5 seconds ----------

var messages = document.querySelectorAll(".message");

function hideLater(message) {
  setTimeout(function () {
    message.style.display = "none";
  }, 5000);
}

for (var i = 0; i < messages.length; i++) {
  hideLater(messages[i]);
}


// ---------- "Show" and "Hide" buttons next to password boxes ----------

var toggles = document.querySelectorAll(".show-password");

function togglePassword(button) {
  var input = document.getElementById(button.getAttribute("data-target"));

  if (input.type === "password") {
    input.type = "text";
    button.textContent = "Hide";
  } else {
    input.type = "password";
    button.textContent = "Show";
  }
}

for (var j = 0; j < toggles.length; j++) {
  toggles[j].addEventListener("click", function () {
    togglePassword(this);
  });
}
