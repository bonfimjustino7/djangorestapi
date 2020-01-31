
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
    $('<strong id="dicas">Dicas: <p id="obs"></p></strong>').appendTo('#tabs-2'); //criando o elemento
    $('#dicas').hide(); // ocultando o elemento

    $('.dynamic-material_set select').change(function () {
        getDica($(this).val())
    });
    $('#id_videocase').focusin(function () {
       getDicaByName('Videocase');
    });
    $('#id_apresentacao').focusin(function () {
       getDicaByName('Apresentação');
    });

});