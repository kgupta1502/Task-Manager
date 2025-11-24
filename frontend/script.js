// Change theme on button click
function toggleTheme() {
    let body = document.body;

    if (body.style.backgroundColor === "white" || body.style.backgroundColor === "") {
        body.style.backgroundColor = "#2c3e50";
        body.style.color = "white";
    } else {
        body.style.backgroundColor = "white";
        body.style.color = "black";
    }
}

// Form validation
let form = document.querySelector("form");

form.addEventListener("submit", function (event) {
    event.preventDefault();

    let name = document.querySelector('input[type="text"]').value;
    let email = document.querySelector('input[type="email"]').value;

    if (name === "" || email === "") {
        alert("Please fill in all fields!");
    } else {
        alert("Thank you, " + name + "! Message sent.");
        form.reset();
    }
});

// Add a click counter
let counter = 0;

function countClicks() {
    counter++;
    document.getElementById("clickCount").textContent = "Clicks: " + counter;
}
