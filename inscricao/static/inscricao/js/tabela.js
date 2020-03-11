
function contarSelects(){
    return document.querySelectorAll('.dynamic-material_set .field-tipo p').length
}
function contarColunas(){
    return document.querySelectorAll('.module table thead tr th').length

}

jQuery(document).ready(function ($) {
    //alert(contarColunas());
    $('.module table thead').remove();
    $('<thead><tr></tr></tr></thead>').insertBefore('.module table tbody');
    $('<th class="original"></th>').appendTo('.module table thead tr');
    $('<th>Tipo</th>').appendTo('.module table thead tr');
    $('<th>Arquivo/URL</th>').appendTo('.module table thead tr');
    $('<th>Apagar?</th>').appendTo('.module table thead tr');

    for(var i = 0; i < contarSelects(); i++){
        var tipo = $(`#material_set-${i} td.field-tipo p`).html();
        var arquivo = $(`#material_set-${i} td.field-arquivo p`).html();
        var url = $(`#material_set-${i} td.field-url p`).html();
        var original = $(`#material_set-${i} td.original p`).html();
        //$(`#material_set-${i}`).remove();
        console.log();
        var id = original.trim().split('(')[1].split(')')[0];
        // $(`<tr class="form-row row1 has_original dynamic-material_set" id="material_set-${i}">`).appendTo('.module table tbody')

        $(`#material_set-${i} .field-arquivo`).remove();
        $(`#material_set-${i} .field-url`).remove();
        $(`#material_set-${i} .delete`).remove();
        $(`#material_set-${i} .field-tipo`).remove();

        $(`<td class="field-tipo"><p>${tipo} <span id="pk_material" style="display: none">${id}</span></p></td>`).appendTo(`#material_set-${i}`);

        if(arquivo){
            $(`<td class="field-arquivo"><p>${arquivo}</p></td>`).appendTo(`#material_set-${i}`);
        }
        if(url){
              $(`<td class="field-url"><p>${url}</p></td>`).appendTo(`#material_set-${i}`);
        }
        $(`<td class="delete"><a href="/delete/${id}?to=/admin/inscricao/inscricao/${$('#pk').html()}/change/#tabs-2"><input type="button" class="deletelink" style="background-color: #ba2121" name="material_set-${i}-DELETE" id="delete-material" value="Apagar"></a></td>`).appendTo(`#material_set-${i}`);
    }
});