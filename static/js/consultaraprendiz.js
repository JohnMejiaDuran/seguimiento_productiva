

// window.addEventListener('DOMContentLoaded', (event) => {
//   const archivoInput = document.querySelector('input[type="file"]');
//   const cuadroBlanco = document.querySelector('.cuadro-blanco'); // Use the ID to select the element

//   archivoInput.addEventListener('change', (e) => {
//       const fileInput = e.target;
//       const allowedExtensions = /(\.xlsx|\.xls)$/i; // Extensión permitida (Excel)

//       if (!allowedExtensions.exec(fileInput.value)) {
//           alert('Por favor, seleccione un archivo con la extensión .xlsx o .xls (Excel).');
//           fileInput.value = ''; // Limpia el campo de entrada de archivo
//           return;
//       }
//       // Show the cuadro-blanco div
      
//   });
// });

function consultaraprendiz(){
    var emergentes = document.getElementsByClassName("centrarformulario");
    for (var i = 0; i < emergentes.length; i++){
        emergentes[i].style.display = "flex";
    }
}

function cerrarconsultaprendiz(){
    var emergentes = document.getElementsByClassName("centrarformulario");
    for (var i = 0; i < emergentes.length; i++){
        emergentes[i].style.display = "none";
    }
}