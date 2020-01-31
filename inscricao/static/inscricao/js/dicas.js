
function getDica(id){
    $.get(`/dica_material/${id.trim()}/`, function (res) {
            if(!res.dica){
              document.getElementById('dicas').style.display = 'none';
            }
            document.getElementById('obs').innerText = res.dica;
            console.log(res)
        })
}
function getDicaByName(name){
    $.get(`/dica_material/name/${name}/`, function (res) {
            if(!res.dica){
                $('#dicas').hide();
            }
            document.getElementById('obs').innerText = res.dica;
            console.log(res)
        })
}
$(document).ready(function () {
    $('<strong id="dicas">Dicas: <p id="obs"></p></strong>').appendTo('#tabs-2'); //criando o elemento
    document.getElementById('dicas').style.display = 'none'; // ocultando o elemento

    $('.dynamic-material_set select').change(function () {
        document.getElementById('dicas').style.display = 'inline-block';
        getDica($(this).val())
    })
    $('#id_videocase').focusin(function () {
       $('#dicas').show();
       getDicaByName('Videocase');

    })
    $('#id_apresentacao').focusin(function () {
       $('#dicas').show();
       getDicaByName('Apresentação');

    })

})