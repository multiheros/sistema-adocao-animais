from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Animal
from .forms import AnimalForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def animal_list(request):
    qs = Animal.objects.all().order_by('-id')
    species = request.GET.get('species')
    adopted = request.GET.get('adopted')
    q = request.GET.get('q')
    if species:
        qs = qs.filter(species=species)
    if adopted in {'true', 'false'}:
        qs = qs.filter(adopted=(adopted == 'true'))
    if q:
        qs = qs.filter(name__icontains=q)
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'animals': page_obj.object_list,
        'page_obj': page_obj,
        'filter_species': species or '',
        'filter_adopted': adopted or '',
        'filter_q': q or '',
    }
    return render(request, 'animals/animal_list.html', context)

def animal_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    return render(request, 'animals/animal_detail.html', {'animal': animal})

@login_required
def animal_create(request):
    if request.method == "POST":
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.created_by = request.user
            animal.save()
            messages.success(request, 'Animal criado com sucesso!')
            return redirect('animal_list')
    else:
        form = AnimalForm()
    return render(request, 'animals/animal_form.html', {'form': form, 'animal': None})

@login_required
def animal_update(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    # Não permitir edição de animal já adotado
    if animal.adopted:
        messages.warning(request, 'Este animal já foi adotado e não pode ser editado.')
        return redirect('animal_detail', pk=animal.pk)
    if not (request.user.is_staff or request.user.is_superuser or animal.created_by_id == request.user.id):
        raise PermissionDenied("Você não tem permissão para editar este animal.")
    if request.method == "POST":
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal atualizado com sucesso!')
            return redirect('animal_detail', pk=animal.pk)
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'animals/animal_form.html', {'form': form, 'animal': animal})

@login_required
def animal_delete(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    # Não permitir exclusão de animal já adotado
    if animal.adopted:
        messages.warning(request, 'Este animal já foi adotado e não pode ser excluído.')
        return redirect('animal_detail', pk=animal.pk)
    if not (request.user.is_staff or request.user.is_superuser or animal.created_by_id == request.user.id):
        raise PermissionDenied("Você não tem permissão para excluir este animal.")
    if request.method == "POST":
        animal.delete()
        messages.success(request, 'Animal excluído com sucesso!')
        return redirect('animal_list')
    return render(request, 'animals/animal_confirm_delete.html', {'animal': animal})