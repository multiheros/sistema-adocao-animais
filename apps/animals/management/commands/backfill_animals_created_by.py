from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.animals.models import Animal


class Command(BaseCommand):
    help = "Atribui created_by a registros de Animal existentes (útil após adicionar o campo)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Usuário ao qual atribuir como criador (created_by).",
        )
        parser.add_argument(
            "--only-null",
            action="store_true",
            help="Atualiza apenas registros com created_by nulo (padrão).",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Ignora --only-null e atualiza todos os registros.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra quantos registros seriam afetados sem alterar nada.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        only_null = options["only-null"]
        update_all = options["all"]
        dry_run = options["dry-run"]

        if update_all:
            only_null = False

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"Usuário '{username}' não encontrado.")

        qs = Animal.objects.all()
        if only_null:
            qs = qs.filter(created_by__isnull=True)

        count = qs.count()
        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry-run: {count} registros seriam atualizados para created_by={user.id} ({user.username})."))
            return

        updated = qs.update(created_by_id=user.id)
        self.stdout.write(self.style.SUCCESS(f"Registros atualizados: {updated}"))
