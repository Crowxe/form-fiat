(function ($) {
    'use strict';
    /*==================================================================
        [ Daterangepicker ]*/
    try {
        $('.js-datepicker').daterangepicker({
            "singleDatePicker": true,
            "showDropdowns": true,
            "autoUpdateInput": false,
            locale: {
                format: 'DD/MM/YYYY'
            },
        });
    
        var myCalendar = $('.js-datepicker');
        var isClick = 0;
    
        $(window).on('click',function(){
            isClick = 0;
        });
    
        $(myCalendar).on('apply.daterangepicker',function(ev, picker){
            isClick = 0;
            $(this).val(picker.startDate.format('DD/MM/YYYY'));
    
        });
    
        $('.js-btn-calendar').on('click',function(e){
            e.stopPropagation();
    
            if(isClick === 1) isClick = 0;
            else if(isClick === 0) isClick = 1;
    
            if (isClick === 1) {
                myCalendar.focus();
            }
        });
    
        $(myCalendar).on('click',function(e){
            e.stopPropagation();
            isClick = 1;
        });
    
        $('.daterangepicker').on('click',function(e){
            e.stopPropagation();
        });
    
    
    } catch(er) {console.log(er);}
    /*[ Select 2 Config ]
        ===========================================================*/
    
    try {
        var selectSimple = $('.js-select-simple');
    
        selectSimple.each(function () {
            var that = $(this);
            var selectBox = that.find('select');
            var selectDropdown = that.find('.select-dropdown');
            selectBox.select2({
                dropdownParent: selectDropdown
            });
        });
    
    } catch (err) {
        console.log(err);
    }
    

})(jQuery);

const canvas = document.getElementById('signature-pad');
const ctx = canvas.getContext('2d');
const signaturePad = new SignaturePad(canvas);
let hasDrawn = false; // Variable para rastrear si ya se ha dibujado en el canvas

// Ajustar el tamaño del canvas y dibujar el "placeholder"
function setupCanvas() {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);
    ctx.font = '20px Arial';
    ctx.fillStyle = '#A9A9A9';
    ctx.textAlign = 'center';
    ctx.fillText('Firme aquí', canvas.width / 2, canvas.height / 2);
}

// Configuración inicial
setupCanvas();
signaturePad.minWidth = 1;
signaturePad.maxWidth = 3;
signaturePad.penColor = "rgb(0, 0, 0)";

// Evento para limpiar el "placeholder" al comenzar a dibujar
signaturePad.addEventListener("beginStroke", () => {
    if (!hasDrawn) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hasDrawn = true;
    }
});

// Evento para el botón de limpiar
document.getElementById('clear-pad').addEventListener('click', () => {
    signaturePad.clear();
    setupCanvas();
    hasDrawn = false; // Restablecer el indicador al limpiar el canvas
});
