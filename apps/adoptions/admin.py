from django.contrib import admin
from .models import Adoption
from django.db import transaction

@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ("id", 'animal', 'adopter', 'adoption_date', 'status')
    search_fields = ('animal__name', 'adopter__username')
    list_filter = ('status', 'adoption_date')
    ordering = ('-adoption_date',)
    actions = ("approve_adoptions", "reject_adoptions")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('animal', 'adopter')

    @admin.action(description="Aprovar adoções selecionadas")
    def approve_adoptions(self, request, queryset):
        from django.contrib import messages
        approved = 0
        with transaction.atomic():
            for adoption in queryset.select_related('animal'):
                animal = adoption.animal
                # Se já existe uma adoção aprovada para este animal, pule
                if animal.adopted and adoption.status != 'approved':
                    continue
                adoption.status = 'approved'
                adoption.save(update_fields=['status'])
                if not animal.adopted:
                    animal.adopted = True
                    animal.save(update_fields=['adopted'])
                approved += 1
        self.message_user(request, f"{approved} adoção(ões) aprovada(s).", level=messages.SUCCESS)

    @admin.action(description="Rejeitar adoções selecionadas")
    def reject_adoptions(self, request, queryset):
        from django.contrib import messages
        rejected = queryset.update(status='rejected')
        self.message_user(request, f"{rejected} adoção(ões) rejeitada(s).", level=messages.WARNING)