
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


$(document).ready(function() {
    $('#aprobados').DataTable({
        paging: false,
        language: {
            processing: "Tratamiento en curso...",
            search: "Buscar&nbsp;:",
            lengthMenu: "Agrupar de _MENU_ items",
            info: "Mostrando un total de _TOTAL_ aprendices",
            infoEmpty: "No existen datos.",
            infoFiltered: "(filtrado de _MAX_ elementos en total)",
            infoPostFix: "",
            loadingRecords: "Cargando...",
            zeroRecords: "No se encontraron datos con tu busqueda",
            emptyTable: "No hay datos disponibles en la tabla.",
            paginate: {
                first: "Primero",
                previous: "Anterior",
                next: "Siguiente",
                last: "Ultimo"
            },
            aria: {
                sortAscending: ": active para ordenar la columna en orden ascendente",
                sortDescending: ": active para ordenar la columna en orden descendente"
            }
        },
    })
    $('.tabla').DataTable({
        language: {
            processing: "Tratamiento en curso...",
            search: "Buscar&nbsp;:",
            lengthMenu: "Agrupar de _MENU_ items",
            info: "Mostrando del item _START_ al _END_ de un total de _TOTAL_ items",
            infoEmpty: "No existen datos.",
            infoFiltered: "(filtrado de _MAX_ elementos en total)",
            infoPostFix: "",
            loadingRecords: "Cargando...",
            zeroRecords: "No se encontraron datos con tu busqueda",
            emptyTable: "No hay datos disponibles en la tabla.",
            paginate: {
                first: "Primero",
                previous: "Anterior",
                next: "Siguiente",
                last: "Ultimo"
            },
            aria: {
                sortAscending: ": active para ordenar la columna en orden ascendente",
                sortDescending: ": active para ordenar la columna en orden descendente"
            }
        },
        
    });
});

let isFirstClick = true;

function scrollOrBack() {
    // Verifica la posición actual del scroll
    if (window.scrollY === 0) {
        // Desplaza al inicio del scroll si está en la parte superior
        window.scrollTo(0, 0);
    } else {
        // Vuelve atrás en la historia si no está en la parte superior
        window.history.back();
    }
}


  