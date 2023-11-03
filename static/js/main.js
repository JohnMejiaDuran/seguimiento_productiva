
document.addEventListener('DOMContentLoaded', function() {
    const archivoInput = document.querySelector('input[name="archivo"]');
    const botonEnviar = document.querySelector('#botonEnviar');

    archivoInput.addEventListener('change', function() {
        if (archivoInput.files.length > 0) {
            botonEnviar.removeAttribute('disabled');
        } else {
            botonEnviar.setAttribute('disabled', 'disabled');
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const archivoInput = document.querySelector('input[name="archivo2"]');
    const botonEnviar = document.querySelector('#botonEnviar');

    archivoInput.addEventListener('change', function() {
        if (archivoInput.files.length > 0) {
            botonEnviar.removeAttribute('disabled');
        } else {
            botonEnviar.setAttribute('disabled', 'disabled');
        }
    });
});

const asignarInstructor = document.getElementById("asignarInstructor");
const instructorSelect = document.getElementById("instructorSelect");

instructorSelect.addEventListener("change", function () {
    if (instructorSelect.value) {
        asignarInstructor.disabled = false;
        asignarInstructor.classList.remove("btn-outline-success")
        asignarInstructor.classList.add("btn-success")
    } else {
        asignarInstructor.disabled = true;
        
    }
});