
$(document).ready(function () {
    const qtd = document.querySelectorAll('.has_original').length;
    console.log(qtd)
    for(var i = 0; i < qtd; i++){
        var a = $(`#material_set-${i} .field-arquivo .file-upload`).length
        if(a){
            var ref_img = document.querySelector(`#material_set-${i} td.field-arquivo .file-upload a`).href;
            $(`#material_set-${i} td.field-arquivo p.file-upload`).remove(); //apaga a div atual

            $(`<input type="file" name="material_set-${i}-arquivo" id="id_material_set-${i}-arquivo"/>`).appendTo(`#material_set-${i} td.field-arquivo`);
            $(`<a class="view-file" id="view-file-set-${i}">Visualizar</a>`).appendTo(`#material_set-${i} td.field-arquivo`);
            $(`#view-file-set-${i}`).attr('href', ref_img);
            $(`<span class="clear-file" id="clear-${i}"><input type="checkbox" id="id_material_set-${i}-arquivo-clear_id" name="material_set-${i}-arquivo-clear"><label for="id_material_set-${i}-arquivo-clear_id">Limpar</label></span>`).appendTo(`#material_set-${i} td.field-arquivo`);

        }

    }


});