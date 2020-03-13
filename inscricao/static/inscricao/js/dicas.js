
function getDica(id){
    $.get(`/dica_material/${id.trim()}/`, function (res) {
            if(!res.dica){
              $('#dicas').hide();
            }else {
                $('#dicas').show();
                document.getElementById('obs').innerText = res.dica;
                console.log(res);
            }

        })
}
function getDicaModal(id){
    $.get(`/dica_material/${id.trim()}/`, function (res) {
            if(!res.dica){
              $('#dicas-modal').hide();
            }else {
                $('#dicas-modal').show();
                document.getElementById('obs-modal').innerText = res.dica;
                console.log(res);
            }

        })
}
function getDicaByName(name){
    $.get(`/dica_material/name/${name}/`, function (res) {
            if(!res.dica){
                $('#dicas').hide();
            }else{
                $('#dicas').show();
                 document.getElementById('obs').innerText = res.dica;
            }
            //console.log(res);
        })
}
$(document).ready(function () {
    $('<strong style="display: block; margin-top: 20px" id="dicas">Dicas: <p id="obs"></p></strong>').insertAfter('#tabs-2 .field-apresentacao'); //criando o elemento
    $('#dicas').hide(); // ocultando o elemento
    $('<strong id="dicas-modal">Dicas: <p id="obs-modal"></p></strong>').appendTo('.dialog .modal-body'); //criando o elemento
    $('#dicas-modal').hide(); // ocultando o elemento

    $('.dynamic-material_set select').change(function () {
        getDica($(this).val());
    });
    $('.column1 select').change(function () {
        getDicaModal($(this).val());
    });
    $('#id_videocase').focusin(function () {
       getDicaByName('Videocase');
    });
    $('#id_apresentacao').focusin(function () {
       getDicaByName('Apresentação');
    });

});