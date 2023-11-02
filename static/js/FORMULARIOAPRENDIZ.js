document.addEventListener("DOMContentLoaded", function () {
    const userIcon = document.getElementById("userIcon");
    const menu = document.getElementById("menu");

    userIcon.addEventListener("click", function (event) {
        event.stopPropagation(); // Prevent the click event from propagating to the document body
        menu.style.display = menu.style.display === "block" ? "none" : "block";
    });

    // Close the menu when clicking anywhere outside of it
    document.body.addEventListener("click", function () {
        menu.style.display = "none";
    });

    // Prevent the menu from closing when clicking inside it
    menu.addEventListener("click", function (event) {
        event.stopPropagation();
    });
});
