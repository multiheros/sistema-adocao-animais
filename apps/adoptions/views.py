from django.shortcuts import render, get_object_or_404, redirect
from .models import Adoption
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib import messages
from .forms import AdoptionForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def adoption_list(request):
    qs = Adoption.objects.select_related('animal', 'adopter').all().order_by('-id')
    status = request.GET.get('status')
    q = request.GET.get('q')
    adopter_q = request.GET.get('adopter')
    if status in {'pending', 'approved', 'rejected'}:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(animal__name__icontains=q)
    if adopter_q:
        qs = qs.filter(adopter__username__icontains=adopter_q)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'adoptions/adoption_list.html', {
        'adoptions': page_obj.object_list,
        'page_obj': page_obj,
        'filter_status': status or '',
        'filter_q': q or '',
        'filter_adopter': adopter_q or '',
    })

def adoption_detail(request, pk):
    adoption = get_object_or_404(Adoption, pk=pk)
    return render(request, 'adoptions/adoption_detail.html', {'adoption': adoption})

@login_required
def adoption_create(request):
    if request.method == "POST":
        form = AdoptionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                adoption = form.save(commit=False)
                # Força regras: adoção criada pelo usuário logado, sempre pendente
                adoption.adopter = request.user
                adoption.status = 'pending'
                adoption.save()
                messages.success(request, 'Adoção criada com sucesso!')
                return redirect('adoption_list')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        initial = {}
        if (animal_id := request.GET.get('animal')):
            initial['animal'] = animal_id
        if request.user.is_authenticated:
            initial['adopter'] = request.user.pk
    form = AdoptionForm(initial=initial, user=request.user)
    return render(request, 'adoptions/adoption_form.html', {'form': form, 'adoption': None})

@login_required
def adoption_update(request, pk):
    adoption = get_object_or_404(Adoption, pk=pk)
    # Apenas o criador do animal ou admin pode alterar o status (aprovar/rejeitar)
    is_admin = request.user.is_staff or request.user.is_superuser
    is_animal_owner = getattr(adoption.animal, 'created_by_id', None) == request.user.id
    if not (is_admin or is_animal_owner):
        raise PermissionDenied('Você não tem permissão para alterar o status desta adoção.')
    if request.method == "POST":
        form = AdoptionForm(request.POST, instance=adoption, user=request.user)
        if form.is_valid():
            try:
                updated = form.save(commit=False)
                # Trava animal e adotante para não serem alterados por engano
                updated.animal_id = adoption.animal_id
                updated.adopter_id = adoption.adopter_id
                updated.save()
                messages.success(request, 'Adoção atualizada com sucesso!')
                return redirect('adoption_detail', pk=adoption.pk)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = AdoptionForm(instance=adoption, user=request.user)
    return render(request, 'adoptions/adoption_form.html', {'form': form, 'adoption': adoption})

@login_required
def adoption_delete(request, pk):
    adoption = get_object_or_404(Adoption, pk=pk)
    # Apenas o criador do animal ou admin pode excluir a adoção
    is_admin = request.user.is_staff or request.user.is_superuser
    is_animal_owner = getattr(adoption.animal, 'created_by_id', None) == request.user.id
    if not (is_admin or is_animal_owner):
        raise PermissionDenied('Você não tem permissão para excluir esta adoção.')
    if request.method == "POST":
        adoption.delete()
        messages.success(request, 'Adoção excluída com sucesso!')
        return redirect('adoption_list')
    return render(request, 'adoptions/adoption_confirm_delete.html', {'adoption': adoption})