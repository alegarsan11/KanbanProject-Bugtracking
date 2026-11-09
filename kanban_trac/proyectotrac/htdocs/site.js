jQuery(document).ready(function($) {
    function toggleCustomFields() {
        // Usamos el ID directo #type que es el estándar en Trac
        var tipoSeleccionado = $('#field-type').val();
        console.log("Tipo seleccionado:", tipoSeleccionado);
        
        var $campoMockup = $('#field-feat_mockup, [name="field_feat_mockup"]').closest('tr, .field, div.field');
        
        if (tipoSeleccionado === 'ECR') {
            $campoMockup.show();
            console.log("LOES");
        } else {
            console.log("NOLOES");
            $campoMockup.hide();
        }
    }
    
    // Ejecutar al cargar y al cambiar
    toggleCustomFields();
    
    $(document).on('change', '#field-type', function() {
        toggleCustomFields();
    });
});