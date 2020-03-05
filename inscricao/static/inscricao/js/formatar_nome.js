

$(document).ready(function () {
    $('#id_nome').attr('style', "text-transform: uppercase;")
        $('#id_nome').on("change", function () {
                nome = $('#id_nome').val();
                p = ["LTDA", "PROPAGANDA", "COMUNICAÇÃO", "CRIAÇÃO", "PROMOÇÕES", "DESIGN"]
                nome_final = ''
                nome_array = nome.split(' ')
                for (x in nome_array) {
                   if (jQuery.inArray( nome_array[x].toUpperCase(), p )==-1) {
                        nome_final = nome_final + ' ' + nome_array[x]
                    }
                }
                nome_final = nome_final.trim()
                $('#id_nome').val(nome_final);
        });
});