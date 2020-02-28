from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
import json
from base.models import Premio, Premiacao, Regional, TipoMaterial
from colunistas import settings
from inscricao.models import Material, Empresa, EmpresaUsuario, Usuario, Inscricao


def tipo_materiais(request, id):
    premiacao = Premiacao.objects.get(id=id)
    context = premiacao.materiais.all().values_list('id', 'descricao', 'arquivo', 'url').order_by('id')

    result = []
    for reg in context:
        result.append({
            'id': reg[0],
            'text': reg[1],
            'arquivo': reg[2],
            'url': reg[3],
        })
    return HttpResponse(json.dumps(result), content_type='application/json')

def dica_materiais(request, id):
    material = TipoMaterial.objects.get(id=id)
    return HttpResponse(json.dumps({'dica': material.dicas}), content_type='application/json')

def dica_materiais_by_name(request, name):
    material = TipoMaterial.objects.get(descricao=name)
    return HttpResponse(json.dumps({'dica': material.dicas}), content_type='application/json')


def filtrar_estados(request, id):
    regional = Regional.objects.get(id=id)
    estados = regional.estados.split(',')
    estados = [estado.strip(' ') for estado in estados]
    return HttpResponse(json.dumps(estados), content_type='application/json')

def get_tipo_materiais(request, id):
    lista_materiais = list(Material.objects.filter(inscricao=id).values('tipo'))
    return HttpResponse(json.dumps(lista_materiais), content_type='application/json')

def formularios_custos(request):
    messages.warning(request, 'Rotina ainda não foi implementada.')
    return redirect('/')

def inscricoes_cadastradas(request):
    messages.warning(request, 'Rotina ainda não foi implementada.')
    return redirect('/')

def custos_total(empresa):
    total = 0
    inscricoes = Inscricao.objects.filter(empresa=empresa)
    for inscricao in inscricoes:
        total += inscricao.material_set.all().count() * 100

    return total

def finalizar2(request, *args, **kwargs):
    context = {}
    context['finalizar'] = True
    erros = 0
    if request.POST.get('_send'):
        file = request.FILES.get('comprovante')
        filename = settings.COMPROVANTE_URL + '/' + file.name
        default_storage.save(filename, file) # salvando comprovante
        empresa = Empresa.objects.get(id=request.POST['empresa'])
        empresa.status = 'F'
        empresa.save()
        messages.success(request, 'Inscrição Finalizada.')
        return redirect('/')
    else:
        empresa_id = request.POST.get('empresa')
        if empresa_id:
            empresa = Empresa.objects.get(id=empresa_id)
        else:
            empresa = args[0]

        context['empresa'] = empresa
        context['custo_total'] = '%.2f' % float(custos_total(empresa))
        for inscricao in empresa.inscricao_set.all():
            if inscricao.status == 'A':
                erros += 1
            if erros > 0:
                context['finalizar'] = False
                messages.warning(request, 'Existem %d inscrições com erro.' % erros)

        return render(request, 'finalizar.html', {'context': context})

@login_required
def finalizar(request):
    context = {}

    if request.POST:
        return finalizar2(request)
    else:
        if request.user.is_active:
            usuario = Usuario.objects.filter(user=request.user)
            empresa_usuario = EmpresaUsuario.objects.filter(usuario=usuario, empresa__status='A')
            if len(empresa_usuario) > 1:
                empresas = list(empresa_usuario.values_list('empresa', 'empresa__nome'))
                empresas_aux = []
                for empresa in empresas:
                    empresas_aux.append({
                        'id': empresa[0],
                        'nome': empresa[1]
                    })
                context['empresas'] = empresas_aux
                return render(request, 'escolher_empresa.html', {'context': context})

            elif len(empresa_usuario) == 1:
                return finalizar2(request, empresa_usuario.get().empresa)

            else:
                messages.error(request, 'Você não tem nenhuma empresa inscrita.')
                return redirect('/')