
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

const asignarInstructor = document.getElementById("asignar_instructor");
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


// $('#asignar_instructor').on('click', function() {
//     var datosAEnviar = [];

//     $('#aprobados tbody tr').each(function(index) {
//         var documento = $(this).find('input[name="documento' + index + '"]').val();
//         var nombre = $(this).find('input[name="nombre' + index + '"]').val();
//         var apellido = $(this).find('input[name="apellido' + index + '"]').val();
//         var alternativa = $(this).find('select[name="alternativa' + index + '"]').val();

//         datosAEnviar.push({
//             documento: documento,
//             nombre: nombre,
//             apellido: apellido,
//             alternativa: alternativa
//         });
//     });

//     // Enviar los datos mediante AJAX con el tipo de contenido 'application/json'
//     $.ajax({
//         type: 'POST',
//         url: '/guardar_aprendices',
//         contentType: 'application/json; charset=utf-8', // Configurar el tipo de contenido
//         dataType: 'json', // Esperar datos JSON en la respuesta del servidor
//         data: JSON.stringify({ datos: datosAEnviar }),
//         success: function(response) {
//             alert(response); // Muestra la respuesta del servidor
//         },
//         error: function(error) {
//             console.error('Error al enviar los datos:', error);
//         }
//     });
// });

