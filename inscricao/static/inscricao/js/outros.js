function carregar(cont){
             $.get(`/tipos_materiais/${$('#id_premiacao').val()}`, function (res) {
                for(var i = 0; i < cont; i++){
                    var select = document.getElementById(`id_material_set-${i}-tipo`)
                    var val_select = $(select).val()
                    $(select).empty()
                    $(select).append($('<option></option>').attr("value", '').text('------'))
                    $.each(res, function (id, value) {
                        if(val_select == value.id){
                            $(select).append($('<option value=" '+value.id+' " selected="selected">'+ value.text+'</option>'))
                        }
                        else{
                            $(select).append($('<option value=" '+value.id+' ">'+ value.text+'</option>'))
                        }
                    })
                }
            })
        }
        function habilarCampos(valor, campo, classe){
            campo = campo.split('tipo')
            var arquivo = campo[0] + 'arquivo'
            var arquivo_cpy = campo[0] + 'arquivo-cpy'
            var url = campo[0] + 'url'
            classe = classe.split('-')
            classe = classe[0] +'-'+ classe[1]

            $.get(`/tipos_materiais/${$('#id_premiacao').val()}`, function (res) {
                 $.each(res, function (id, value) {
                    if(valor == value.id){
                        if(value.url != true){
                            $(`.dynamic-material_set .field-url input#${url}`).prop('disabled', true)
                            console.log(value.url)
                        }
                        else{
                            $(`.dynamic-material_set .field-url input#${url}`).prop('disabled', false)
                            console.log(value.url)
                        }
                        if(value.arquivo != true){
                            $(`.dynamic-material_set .field-arquivo input#${arquivo}`).prop('disabled', true);
                            $(`.dynamic-material_set .field-arquivo #${arquivo_cpy}`).addClass('file-disabled');
                            $(`.dynamic-material_set .field-arquivo #${arquivo}-label`).addClass('label-disabled');

                        }
                        else{
                           $(`.dynamic-material_set .field-arquivo input#${arquivo}`).prop('disabled', false);
                           $(`.dynamic-material_set .field-arquivo #${arquivo_cpy}`).removeClass('file-disabled');
                           $(`.dynamic-material_set .field-arquivo #${arquivo}-label`).removeClass('label-disabled');
                        }
                    }
                 })
            })
        }
        function carregarUm(cont){
            //console.log(cont)
             $.get(`/tipos_materiais/${$('#id_premiacao').val()}`, function (res) {
                    var select = document.getElementById(`id_material_set-${cont-1}-tipo`)
                    $(select).empty()
                    $(select).append($('<option></option>').attr("value", '').text('------'))
                    $.each(res, function (id, value) {
                        $(select).append($('<option></option>').attr("value", value.id).text(value.text))
                    })
            })
        }
        function contarSelects(){
            return document.querySelectorAll('.dynamic-material_set .field-tipo select').length
        }
        function contarAgencias(){
            return document.querySelectorAll('.dynamic-empresaagencia_set .field-uf select').length
        }
        $(document).ready(function () {

            // modal

            $('<a href="#" type="button" class="mostrar button default" id="id_mostrar"><img src="../../../../../static/admin/img/icon-addlink.svg" alt=""> Adicionar Material</a>').insertBefore(`#tabs-2 .inline-related .module `);
            $(`.dialog .modal-body .column1 label`).attr({'for': `id-tipo`});
            $(`.dialog .modal-body .column1 select`).attr({'id':`id-tipo`});
            //$(`.dialog .modal-body .column2 label`).attr({'for':`id_material_set-${contarSelects()-1}-arquivo`});
            $(`.dialog .modal-body .column2 label span.botao`).attr({'id':`botao_file`});
            $(`.dialog .modal-body .column2 label span.label`).attr({'id':`label-file`});

            $(`fieldset.module tr#material_set-${contarSelects()-1}`).css('display', 'none'); // removendo o ultimo tr


            $('.dialog .modal-body .column1 select').change(function () {
                $('.dialog .modal-content .modal-footer button').removeAttr('disabled');
                var valor = $(this).val();
                $.get(`/tipos_materiais/${$('#id_premiacao').val()}`, function (res){
                    $.each(res, function (id, value) {
                        if (valor == value.id) {
                            if (!value.arquivo) {
                                $('.dialog .modal-body .column2').hide();
                                $('.dialog .modal-body .column3').show();
                            }
                            else{
                                $('.dialog .modal-body .column2').show();
                                $('.dialog .modal-body .column3').hide();
                            }
                        }
                    })
                });
            });
            $.get(`/tipos_materiais/${$('#id_premiacao').val()}`, function (res) {
                    var select = document.getElementById('id-tipo');
                    $(select).empty();
                    $(select).append($('<option></option>').attr("value", '').text('------'))
                    $.each(res, function (id, value) {
                        $(select).append($('<option></option>').attr("value", value.id).text(value.text))
                    })
            });
            $('#id_premiacao').change(function () {
                $.get(`/tipos_materiais/${$(this).val()}`, function (res) {
                    var select = document.getElementById('id-tipo');
                    $(select).empty();
                    $(select).append($('<option></option>').attr("value", '').text('------'))
                    $.each(res, function (id, value) {
                        $(select).append($('<option></option>').attr("value", value.id).text(value.text))
                    })
                })
            });

             // Mudando nome do arquivo selecionado
            $('.dialog .modal-body .column2 .botao').click(function (e) {
               $('.dialog .modal-body .column2 input#file').change(function () {
                    var val = $(this).val().split('\\')[2];
                    if (val)
                        document.getElementById('label-file').innerHTML = val ;
                    else
                        document.getElementById(`label-file`).innerHTML = 'Nenhum arquivo selecionado' ;
                })
            });

             //get_tipo(contarSelects());
             carregar(contarSelects());
             $('#id_premiacao').change(function () {
                 carregar(contarSelects())
             });

            $('.add-row').click(function () {
               carregarUm(contarSelects());
                 $('.dynamic-material_set  td.field-tipo select').change(function (event) {
                    var campo = event.target.id
                    var classe = event.target.name
                    habilarCampos($(this).val(), campo, classe)
                })
            });

            $('.dynamic-material_set  td.field-tipo select').change(function (event) {
                //console.log($(this).val())
                console.log(event.target.id)
                 var campo = event.target.id
                // //document.querySelector('.dynamic-material_set .field-tipo select').className;
                var classe = event.target.name
                //console.log($(this).val())
                 habilarCampos($(this).val(), campo, classe)
            })
            $('.mostrar').click(function () {
               $('.dialog').css('display', 'block');
            });

            // $(`<select name="${contarSelects()}"></select>'`).appendTo('.dialog .modal-body .column1')

            // Ao carregar a página execulta a validação dos materiais
            $.get(`/tipos_materiais/${$('#id_premiacao').val()}`, function (res) {
                for(var i = 0; i < document.querySelectorAll('.has_original').length; i++) {
                    const valor = $(`select#id_material_set-${i}-tipo`).val();
                    $.each(res, function (id, value) {
                        if (valor == value.id) {
                            if (value.arquivo != true) {
                                $(`.dynamic-material_set .field-arquivo input#id_material_set-${i}-arquivo`).prop('disabled', true);
                                $(`.dynamic-material_set .field-arquivo #id_material_set-${i}-arquivo-cpy`).addClass('file-disabled');
                                $(`.dynamic-material_set .field-arquivo #id_material_set-${i}-arquivo-label`).addClass('label-disabled');
                                console.log(value.arquivo)
                            } else {
                                $(`.dynamic-material_set .field-arquivo input#id_material_set-${i}-arquivo`).prop('disabled', false);
                                $(`.dynamic-material_set .field-arquivo #id_material_set-${i}-arquivo-cpy`).removeClass('file-disabled');
                                $(`.dynamic-material_set .field-arquivo #id_material_set-${i}-arquivo-label`).removeClass('label-disabled');
                                console.log(value.arquivo)
                            }
                            if(value.url != true){
                                $(`.dynamic-material_set .field-url input#id_material_set-${i}-url`).prop('disabled', true);
                                console.log(value.url)
                            }
                            else{
                                $(`.dynamic-material_set .field-url input#id_material_set-${i}-url`).prop('disabled', false);
                                console.log(value.url)
                            }
                        }
                    });
                }
            });
          $('#tabs-4 .module h2').remove();
        });
        function get_tipo(cont){
            var id = window.location.href.split('/')[6];
            console.log(id);
             $.get(`/get_tipo_materiais/${id}/`, function (res) {
                 console.log(res);
                for(var i = 0; i < cont; i++){
                    var select = document.getElementById(`id_material_set-${i}-tipo`); // pega o select
                    var c = document.querySelectorAll(`#id_material_set-${i}-tipo option`).length; // conta quantos options existe
                    for(var j = 0; j < c; j++){
                        //console.log(res[i]);
                        if(res[i]){
                            var id_request = res[i].tipo;
                             if(id_request == select.options[j].value){
                                //console.log(select.options[j].value);
                                 $(select.options[j]).attr('selected', '');
                                 //console.log(id_request);
                             }
                        }

                    }

                }
            })
        }
    $(window).on('pageshow', function(){
        console.info('Entered the page!');
         get_tipo(contarSelects())
    });