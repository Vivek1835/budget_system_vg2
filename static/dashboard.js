// dashboard.js - the greeting, the ring and the bars on the Overview page.


// ---------- Greeting that depends on the time of day ----------

var greeting = document.getElementById("greeting");
var name = greeting.getAttribute("data-name");
var hour = new Date().getHours();
var word = "Hi";

if (hour < 5) {
  word = "Good night";
} else if (hour < 12) {
  word = "Good morning";
} else if (hour < 18) {
  word = "Good afternoon";
} else {
  word = "Good evening";
}

greeting.textContent = word + ", " + name;


// ---------- The ring fills up slowly ----------

var ring = document.getElementById("ring");
var target = Number(ring.getAttribute("data-percent"));
var color = ring.getAttribute("data-color");
var current = 0;

function drawRing(percent) {
  ring.style.background = "conic-gradient(" + color + " " + percent + "%, var(--line) 0)";
}

drawRing(0);

var timer = setInterval(function () {
  current = current + 2;

  if (current >= target) {
    current = target;
    clearInterval(timer);
  }

  drawRing(current);
}, 15);


// ---------- The category bars grow from 0 ----------

var bars = document.querySelectorAll(".bar-fill");

for (var i = 0; i < bars.length; i++) {
  bars[i].style.width = "0%";
}

setTimeout(function () {
  for (var j = 0; j < bars.length; j++) {
    bars[j].style.width = bars[j].getAttribute("data-percent") + "%";
  }
}, 100);
