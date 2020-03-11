
function alterarURL(){
    const qtd = document.querySelectorAll('.has_original').length;
    for(var i = 0; i < qtd; i++){
        var a = $(`#material_set-${i} td.field-url p`);
        if(!$(`#material_set-${i} .field-url p`).is(':empty')){
             $(`#material_set-${i} td.field-url p`).remove(); //apaga a div atual
             $(`<a href="${a.html()}" class="view-file" target="_blank" id="view-file-set-${i}">Visualizar</a> <span style="margin-top: 5px!important; display: inline-block; color: #908b8b; font-size: 12px">${a.html()}</span>`).appendTo(`#material_set-${i} td.field-url`);
        }
        // else{
        //     $('<span> - </span>').appendTo(`#material_set-${i} td.field-url p`);
        // }
    }
}

$(document).ready(function () {
    const qtd = document.querySelectorAll('.dynamic-material_set').length;
    const formatos_img = ['jpg', 'jpeg', 'png', 'gif']
    for(var i = 0; i < qtd; i++){
        var a = $(`#material_set-${i} .field-arquivo p a`).length;
        if(a){
            var ref_img = document.querySelector(`#material_set-${i} td.field-arquivo p a`).href;
            console.log(ref_img);
            $(`#material_set-${i} td.field-arquivo p`).remove(); //apaga a div atual
            // $(`<input type="file" name="material_set-${i}-arquivo" id="id_material_set-${i}-arquivo" style="display: none"/>`).appendTo(`#material_set-${i} td.field-arquivo`);
            // $(`<label for="id_material_set-${i}-arquivo"class="file">
            //         <span class="botao" id="id_material_set-${i}-arquivo-cpy">Selecione</span>
            //         <span class="label" id="id_material_set-${i}-arquivo-label">Arquivo Ok</span>
            //     </label>`).appendTo(`#material_set-${i} td.field-arquivo`);

            // var a = $(`#id_material_set-${i}-arquivo`);

            var id = ref_img.split('/')[5].split('.')[1];
            var id_material = $(`#material_set-${i} #pk_material`).html();
            console.log(id);
            if(formatos_img.indexOf(id) > -1){
                $(`<a href="${ref_img}" class="view-file"  id="view-file-set-${i}" data-rel="lightcase">Visualizar</a>`).appendTo(`#material_set-${i} td.field-arquivo`);
            }
            else{
                $(`<a href="/baixar_material/${id_material}/" class="view-file" id="view-file-set-${i}" >Visualizar</a>`).appendTo(`#material_set-${i} td.field-arquivo`);
            }

            $(`<span style="margin-top: 4px!important; display: inline-block; color: #908b8b; font-size: 12px">Arquivo ${id}</span>`).appendTo(`#material_set-${i} td.field-arquivo`);

        }
        // else{
        //     $('<span> - </span>').appendTo(`#material_set-${i} .field-arquivo p`); //apaga a div atual
        //     // $(`<input type="file" name="material_set-${i}-arquivo" id="id_material_set-${i}-arquivo" style="display: none"/>`).appendTo(`#material_set-${i} td.field-arquivo`);
        //     // $(`<label for="id_material_set-${i}-arquivo"class="file" style="width: 250px !important;">
        //     //         <span class="botao" id="id_material_set-${i}-arquivo-cpy">Selecione</span>
        //     //         <span class="label" id="id_material_set-${i}-arquivo-label">Nenhum arquivo selecionado</span>
        //     //     </label>`).appendTo(`#material_set-${i} td.field-arquivo`);
        // }
    }
    alterarURL();
     // $('.add-row a').click(function () {
     //     const qtd = document.querySelectorAll('.dynamic-material_set').length;
     //     console.log(qtd);
     //        $(`#id_material_set-${qtd-1}-arquivo`).remove(); //apaga a div atual
     //        $(`<input type="file" name="material_set-${qtd-1}-arquivo" id="id_material_set-${qtd-1}-arquivo" style="display: none"/>`).appendTo(`#material_set-${qtd-1} td.field-arquivo`);
     //        $(`<label for="id_material_set-${qtd-1}-arquivo"class="file" style="width: 250px !important;">
     //                <span class="botao" id="id_material_set-${qtd-1}-arquivo-cpy">Selecione</span>
     //                <span class="label" id="id_material_set-${qtd-1}-arquivo-label">Nenhum arquivo selecionado</span>
     //            </label>`).appendTo(`#material_set-${qtd-1} td.field-arquivo`);
     //
     //   // Mudando nome do arquivo selecionado
     //     $('.botao').click(function (e) {
     //        const input = e.target.id.split('-cpy')[0];
     //        //console.log(id)
     //       $(`#${input}`).change(function () {
     //            console.log($(this).val().split('\\')[2]);
     //            var val = $(this).val().split('\\')[2];
     //            if (val)
     //                document.getElementById(`${input}-label`).innerHTML = val ;
     //            else
     //                document.getElementById(`${input}-label`).innerHTML = 'Nenhum arquivo selecionado' ;
     //        })
     //    })
     // });
    // // Mudando nome do arquivo selecionado
    // $('.botao').click(function (e) {
    //     const input = e.target.id.split('-cpy')[0];
    //     //console.log(id)
    //    $(`#${input}`).change(function () {
    //         //console.log($(this).val().split('\\')[2]);
    //         var val = $(this).val().split('\\')[2];
    //         if (val)
    //             document.getElementById(`${input}-label`).innerHTML = val ;
    //         else
    //             document.getElementById(`${input}-label`).innerHTML = 'Nenhum arquivo selecionado' ;
    //     })
    // });

    if($('.field-videocase p.url').length){
         var refUrlVideoCase = document.querySelector(`.field-videocase p.url a`).href;
         $('.field-videocase p.url').remove();
         $(`<input type="url" name="videocase" value="${refUrlVideoCase}" class="vURLField" maxlength="512">`).appendTo(`.field-videocase`);
         $(`<a href="${refUrlVideoCase}" target="_blank" class="view-file">Visualizar</a>`).appendTo('.field-videocase');
    }
    if($('.field-apresentacao p.url').length){
        var refUrlApresentacao = document.querySelector(`.field-apresentacao p.url a`).href;
        $('.field-apresentacao p.url').remove();
        $(`<input type="url" name="apresentacao" value="${refUrlApresentacao}" class="vURLField" maxlength="512">`).appendTo(`.field-apresentacao`);
        $(`<a href="${refUrlApresentacao}" target="_blank" class="view-file">Visualizar</a>`).appendTo('.field-apresentacao');
    }




});