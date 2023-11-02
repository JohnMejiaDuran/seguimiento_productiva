
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

