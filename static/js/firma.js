$canvas.addEventListener("mousedown", evento => {
    // En este evento solo se ha iniciado el clic, así que dibujamos un punto
    xAnterior = xActual;
    yAnterior = yActual;
    xActual = obtenerXReal(evento.clientX);
    yActual = obtenerYReal(evento.clientY);
    contexto.beginPath();
    contexto.fillStyle = COLOR_PINCEL;
    contexto.fillRect(xActual, yActual, GROSOR, GROSOR);
    contexto.closePath();
    // Y establecemos la bandera
    haComenzadoDibujo = true;
});

$canvas.addEventListener("mousemove", (evento) => {
    if (!haComenzadoDibujo) {
        return;
    }
    // El mouse se está moviendo y el usuario está presionando el botón, así que dibujamos todo

    xAnterior = xActual;
    yAnterior = yActual;
    xActual = obtenerXReal(evento.clientX);
    yActual = obtenerYReal(evento.clientY);
    contexto.beginPath();
    contexto.moveTo(xAnterior, yAnterior);
    contexto.lineTo(xActual, yActual);
    contexto.strokeStyle = COLOR_PINCEL;
    contexto.lineWidth = GROSOR;
    contexto.stroke();
    contexto.closePath();
});
["mouseup", "mouseout"].forEach(nombreDeEvento => {
    $canvas.addEventListener(nombreDeEvento, () => {
        haComenzadoDibujo = false;
    });
});

const limpiarCanvas = () => {
    // Colocar color blanco en fondo de canvas
    contexto.fillStyle = COLOR_FONDO;
    contexto.fillRect(0, 0, $canvas.width, $canvas.height);
};
limpiarCanvas();
$btnLimpiar.onclick = limpiarCanvas;

$btnDescargar.onclick = () => {
    const enlace = document.createElement('a');
    // El título
    enlace.download = "Firma.png";
    // Convertir la imagen a Base64 y ponerlo en el enlace
    enlace.href = $canvas.toDataURL();
    // Hacer click en él
    enlace.click();
};