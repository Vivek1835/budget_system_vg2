// register.js - checks the sign up form while the user types.
// The server checks everything again, so this is only to help the user.

var form = document.getElementById("signup-form");
var username = document.getElementById("username");
var password = document.getElementById("password");
var confirmBox = document.getElementById("confirm");

var usernameHint = document.getElementById("username-hint");
var passwordHint = document.getElementById("password-hint");
var confirmHint = document.getElementById("confirm-hint");
var strengthFill = document.getElementById("strength-fill");


// Show a hint text in green (ok) or orange (bad)
function showHint(hint, text, isOk) {
  hint.textContent = text;
  if (isOk) {
    hint.className = "hint ok";
  } else {
    hint.className = "hint bad";
  }
}


// Username: 3 to 30 characters, only letters, numbers and _
function checkUsername() {
  var text = username.value.trim();
  var onlyLetters = /^[A-Za-z0-9_]+$/;

  if (text.length === 0) {
    usernameHint.className = "hint";
    usernameHint.textContent = "3 to 30 characters. Letters, numbers and _";
    return false;
  }
  if (text.length < 3) {
    showHint(usernameHint, "Too short. Use at least 3 characters.", false);
    return false;
  }
  if (text.length > 30) {
    showHint(usernameHint, "Too long. Use at most 30 characters.", false);
    return false;
  }
  if (!onlyLetters.test(text)) {
    showHint(usernameHint, "Only letters, numbers and _ are allowed.", false);
    return false;
  }

  showHint(usernameHint, "Looks good.", true);
  return true;
}


// Password: counts points. More points = stronger password.
function checkPassword() {
  var text = password.value;
  var points = 0;

  if (text.length >= 8) {
    points = points + 1;
  }
  if (text.length >= 12) {
    points = points + 1;
  }
  if (/[0-9]/.test(text)) {
    points = points + 1;
  }
  if (/[a-z]/.test(text) && /[A-Z]/.test(text)) {
    points = points + 1;
  }
  if (/[^A-Za-z0-9]/.test(text)) {
    points = points + 1;
  }

  // Draw the strength bar
  strengthFill.style.width = (points * 20) + "%";

  if (points <= 2) {
    strengthFill.style.background = "var(--warning-text)";
  } else if (points <= 3) {
    strengthFill.style.background = "var(--main)";
  } else {
    strengthFill.style.background = "var(--good)";
  }

  if (text.length === 0) {
    passwordHint.className = "hint";
    passwordHint.textContent = "At least 8 characters.";
    return false;
  }
  if (text.length < 8) {
    showHint(passwordHint, "Too short. Use at least 8 characters.", false);
    return false;
  }

  if (points <= 2) {
    showHint(passwordHint, "Okay, but add numbers or capital letters to make it stronger.", true);
  } else if (points <= 3) {
    showHint(passwordHint, "Good password.", true);
  } else {
    showHint(passwordHint, "Strong password.", true);
  }
  return true;
}


// The second password box must be the same as the first
function checkConfirm() {
  if (confirmBox.value.length === 0) {
    confirmHint.className = "hint";
    confirmHint.textContent = "Write the same password again.";
    return false;
  }
  if (confirmBox.value !== password.value) {
    showHint(confirmHint, "The two passwords are not the same.", false);
    return false;
  }

  showHint(confirmHint, "The passwords match.", true);
  return true;
}


username.addEventListener("input", checkUsername);
password.addEventListener("input", function () {
  checkPassword();
  if (confirmBox.value.length > 0) {
    checkConfirm();
  }
});
confirmBox.addEventListener("input", checkConfirm);


// Do not send the form if something is wrong
form.addEventListener("submit", function (event) {
  var usernameOk = checkUsername();
  var passwordOk = checkPassword();
  var confirmOk = checkConfirm();

  if (!usernameOk || !passwordOk || !confirmOk) {
    event.preventDefault();
  }
});
