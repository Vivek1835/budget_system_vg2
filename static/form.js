// form.js - the note counter on the Add and Edit pages.

var note = document.getElementById("description");
var noteCount = document.getElementById("note-count");

function updateCount() {
  noteCount.textContent = note.value.length;
}

note.addEventListener("input", updateCount);
updateCount();
