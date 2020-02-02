
function alterarURL(){
    const qtd = document.querySelectorAll('.has_original').length;
    for(var i = 0; i < qtd; i++){
        var a = $(`#material_set-${i} .field-url .url`).length;
        if(a){
             var ref_url = document.querySelector(`#material_set-${i} td.field-url p.url a`).href;
             $(`#material_set-${i} td.field-url p.url`).remove(); //apaga a div atual
             $(`<input type="url" name="material_set-${i}-url" value="${ref_url}" class="vURLField" maxlength="200" id="id_material_set-${i}-url">`).appendTo(`#material_set-${i} td.field-url`);
        }
    }
}

$(document).ready(function () {
    const qtd = document.querySelectorAll('.has_original').length;
    console.log(qtd)
    for(var i = 0; i < qtd; i++){
        var a = $(`#material_set-${i} .field-arquivo .file-upload`).length
        if(a){
            var ref_img = document.querySelector(`#material_set-${i} td.field-arquivo .file-upload a`).href;
            console.log(ref_img);
            $(`#material_set-${i} td.field-arquivo p.file-upload`).remove(); //apaga a div atual
            $(`<input type="file" name="material_set-${i}-arquivo" id="id_material_set-${i}-arquivo"/>`).appendTo(`#material_set-${i} td.field-arquivo`);
            $(`<a href="${ref_img}" class="view-file" id="view-file-set-${i}" data-rel="lightcase">Visualizar</a>`).appendTo(`#material_set-${i} td.field-arquivo`);
            //$(`#view-file-set-${i}`).attr('href', ref_img);
            $(`<span class="clear-file" id="clear-${i}"><input type="checkbox" id="id_material_set-${i}-arquivo-clear_id" name="material_set-${i}-arquivo-clear"><label for="id_material_set-${i}-arquivo-clear_id">Excluir</label></span>`).appendTo(`#material_set-${i} td.field-arquivo`);
        }
      alterarURL();
    }
    $('.view-file').click(function () {
        $('#navigation-menu').css('position', '')
    })

});