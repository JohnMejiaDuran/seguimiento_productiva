function mostrarDetalles(fila) {
    // Obtén los datos de la fila seleccionada (cambia esto con tus datos reales)
  
    const nombreAprendiz = document.querySelector(`tr:nth-child(${fila}) td:nth-child(3)`).textContent;
    const numeroFicha = document.querySelector(`tr:nth-child(${fila}) td:nth-child(4)`).textContent;
    const programa = document.querySelector(`tr:nth-child(${fila}) td:nth-child(5)`).textContent;
    const fechaInicio = document.querySelector(`tr:nth-child(${fila}) td:nth-child(6)`).textContent;
    const fechaFinal = document.querySelector(`tr:nth-child(${fila}) td:nth-child(7)`).textContent;
    // ... Continúa obteniendo los otros datos

    function agendarVisita() {
        const fechaVisita = document.getElementById("fecha-visita").value;
        const horaVisita = document.getElementById("hora-visita").value;
        
        // Puedes realizar alguna acción para enviar la notificación aquí
        const notificacion = `Visita agendada para el ${fechaVisita} a las ${horaVisita}`;
        alert(notificacion);
    
        // Cierra el popup de detalles
        cerrarDetalles();
    }

    // Rellena el contenido del popup con los datos
    const popup = document.getElementById("detalles-popup");
    popup.innerHTML = `
        <h2>Detalles</h2>
        <p>Nombre Aprendiz : ${nombreAprendiz}</p>
        <p>Numero ficha: ${numeroFicha}</p>
        <p>Programa: ${programa}</p>
        <p>Fecha inicio: ${fechaInicio}</p>
        <p>Fecha final: ${fechaFinal}</p>
        <!-- Agrega los otros datos aquí -->
        <!-- Campos de fecha y hora para agendar la visita -->
        <label for="fecha-visita">Agendar visita:</label>
        <input type="date" id="fecha-visita" name="fecha-visita" required>
        
        <label for="hora-visita">Hora:</label>
        <input type="time" id="hora-visita" name="hora-visita" required>

        <!-- Botón para agendar la visita -->
        <button onclick="agendarVisita()">Agendar Visita</button> 
        <button onclick="cerrarDetalles()">Cerrar</button>
    `;

    // Muestra el popup
    popup.style.display = "block";
}
function cerrarDetalles() {
    // Oculta el popup
    const popup = document.getElementById("detalles-popup");
    popup.style.display = "none";
}
