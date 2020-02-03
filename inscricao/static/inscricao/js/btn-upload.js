
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
    const qtd = document.querySelectorAll('.dynamic-material_set').length;
    const formatos_img = ['jpg', 'jpeg', 'png', 'gif']
    console.log(qtd)
    for(var i = 0; i < qtd; i++){
        var a = $(`#material_set-${i} .field-arquivo .file-upload`).length
        if(a){
            var ref_img = document.querySelector(`#material_set-${i} td.field-arquivo .file-upload a`).href;
            console.log(ref_img);
            $(`#material_set-${i} td.field-arquivo p.file-upload`).remove(); //apaga a div atual
            $(`<input type="file" name="material_set-${i}-arquivo" id="id_material_set-${i}-arquivo" style="display: none"/>`).appendTo(`#material_set-${i} td.field-arquivo`);
            $(`<label for="id_material_set-${i}-arquivo"class="file">
                    <span class="botao" id="id_material_set-${i}-arquivo-cpy">Selecione</span>
                    <span class="label" id="id_material_set-${i}-arquivo-label">Arquivo Ok</span>
                </label>`).appendTo(`#material_set-${i} td.field-arquivo`);

            var a = $(`#id_material_set-${i}-arquivo`);

            var id = ref_img.split('.')[1]
            console.log(id);
            if(formatos_img.indexOf(id) > -1){
                $(`<a href="${ref_img}" class="view-file" id="view-file-set-${i}" data-rel="lightcase">Visualizar</a>`).appendTo(`#material_set-${i} td.field-arquivo`);
            }
            else{
                $(`<a href="/baixar_material/${ref_img.split('/')[5].split('.')[0]}/" class="view-file" id="view-file-set-${i}" >Visualizar</a>`).appendTo(`#material_set-${i} td.field-arquivo`);
            }

            //$(`#view-file-set-${i}`).attr('href', ref_img);
            $(`<span class="clear-file" id="clear-${i}"><input type="checkbox" id="id_material_set-${i}-arquivo-clear_id" name="material_set-${i}-arquivo-clear"><label for="id_material_set-${i}-arquivo-clear_id">Excluir</label></span>`).appendTo(`#material_set-${i} td.field-arquivo`);
        }
        else{
            $(`#id_material_set-${i}-arquivo`).remove(); //apaga a div atual
            $(`<input type="file" name="material_set-${i}-arquivo" id="id_material_set-${i}-arquivo" style="display: none"/>`).appendTo(`#material_set-${i} td.field-arquivo`);
            $(`<label for="id_material_set-${i}-arquivo"class="file" style="width: 250px !important;">
                    <span class="botao" id="id_material_set-${i}-arquivo-cpy">Selecione</span>
                    <span class="label" id="id_material_set-${i}-arquivo-label">Nenhum arquivo selecionado</span>
                </label>`).appendTo(`#material_set-${i} td.field-arquivo`);
        }

      alterarURL();
    }
     $('.add-row a').click(function () {
         const qtd = document.querySelectorAll('.dynamic-material_set').length;
         console.log(qtd);
            $(`#id_material_set-${qtd-1}-arquivo`).remove(); //apaga a div atual
            $(`<input type="file" name="material_set-${qtd-1}-arquivo" id="id_material_set-${qtd-1}-arquivo" style="display: none"/>`).appendTo(`#material_set-${qtd-1} td.field-arquivo`);
            $(`<label for="id_material_set-${qtd-1}-arquivo"class="file" style="width: 250px !important;">
                    <span class="botao" id="id_material_set-${qtd-1}-arquivo-cpy">Selecione</span>
                    <span class="label" id="id_material_set-${qtd-1}-arquivo-label">Nenhum arquivo selecionado</span>
                </label>`).appendTo(`#material_set-${qtd-1} td.field-arquivo`);

       // Mudando nome do arquivo selecionado
         $('.botao').click(function (e) {
            const input = e.target.id.split('-cpy')[0];
            //console.log(id)
           $(`#${input}`).change(function () {
                console.log($(this).val().split('\\')[2]);
                var val = $(this).val().split('\\')[2];
                if (val)
                    document.getElementById(`${input}-label`).innerHTML = val ;
                else
                    document.getElementById(`${input}-label`).innerHTML = 'Nenhum arquivo selecionado' ;
            })
        })
     });
    // Mudando nome do arquivo selecionado
    $('.botao').click(function (e) {
        const input = e.target.id.split('-cpy')[0];
        //console.log(id)
       $(`#${input}`).change(function () {
            //console.log($(this).val().split('\\')[2]);
            var val = $(this).val().split('\\')[2];
            if (val)
                document.getElementById(`${input}-label`).innerHTML = val ;
            else
                document.getElementById(`${input}-label`).innerHTML = 'Nenhum arquivo selecionado' ;
        })
    })

});