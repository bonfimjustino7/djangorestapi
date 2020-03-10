    function remover(arg){
            return arg.replace('-', '')
        }

        $('body').on("submit", function(){
            $('#id_telefone').val(remover($('#id_telefone').val()))
            $('#id_celular').val(remover($('#id_celular').val()))
            $('#id_VP_Telefone').val(remover($('#id_VP_Telefone').val()))
            $('#id_C1_Telefone').val(remover($('#id_C1_Telefone').val()))
            $('#id_C2_Telefone').val(remover($('#id_C2_Telefone').val()))
        });