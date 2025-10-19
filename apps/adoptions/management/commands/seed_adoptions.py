import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.animals.models import Animal
from apps.adoptions.models import Adoption


class Command(BaseCommand):
    help = "Populate the database with sample Adoption records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of adoptions to create (total across statuses unless --per-user is used).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="If provided, will delete existing Adoption records before seeding.",
        )
        parser.add_argument(
            "--mode",
            choices=["mix", "pending", "approved", "rejected"],
            default="mix",
            help="How to distribute adoption statuses.",
        )
        parser.add_argument(
            "--per-user",
            type=int,
            default=0,
            help="Create N adoptions per non-staff user (ignores --count).",
        )
        parser.add_argument(
            "--create-users",
            type=int,
            default=0,
            help="Create N demo users if not enough users exist.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        force = options["force"]
        mode = options["mode"]
        per_user = options["per_user"]
        create_users = options["create_users"]

        User = get_user_model()

        if force:
            self.stdout.write("Deleting existing Adoption records and resetting animal.adopted flags...")
            Adoption.objects.all().delete()
            Animal.objects.update(adopted=False)

        # Ensure there are some users to adopt
        users_qs = User.objects.filter(is_staff=False, is_superuser=False)
        existing_users = list(users_qs)

        # Optionally create demo users
        created_users = []
        if create_users and len(existing_users) < create_users:
            need = create_users - len(existing_users)
            for i in range(need):
                idx = len(existing_users) + i + 1
                u = User.objects.create_user(
                    username=f"demo{idx}",
                    email=f"demo{idx}@example.com",
                    password="Demo12345",
                )
                created_users.append(u)
            self.stdout.write(self.style.SUCCESS(f"Created {len(created_users)} demo users."))

        # Refresh users list after optional creation
        adopters = list(User.objects.filter(is_staff=False, is_superuser=False))
        if not adopters:
            raise CommandError("No regular users found. Create some users or pass --create-users N.")

        animals = list(Animal.objects.all())
        if not animals:
            raise CommandError("No animals found. Run seed_animals first.")

        # Build a pool of animals for pending/rejected where duplicates are fine
        # For approved, we must ensure at most one per animal.
        approved_animals_pool = [a for a in animals]

        def pick_status():
            if mode == "mix":
                return random.choices(["pending", "approved", "rejected"], weights=[5, 3, 2])[0]
            return mode

        # Helper to assign adoption_date within last 120 days
        def random_date_within(days=120):
            delta = random.randint(0, days)
            return date.today() - timedelta(days=delta)

        created = 0
        approved_created = 0
        rejected_created = 0
        pending_created = 0

        def create_one(adopter, status):
            nonlocal approved_created, rejected_created, pending_created
            # Pick animal respecting constraints for approved status
            if status == "approved":
                if not approved_animals_pool:
                    return None
                # Prefer animals not already adopted
                random.shuffle(approved_animals_pool)
                for idx, a in enumerate(approved_animals_pool):
                    # ensure no existing approved for this animal
                    if not Adoption.objects.filter(animal=a, status="approved").exists():
                        animal = a
                        # remove from pool to reduce chances of duplicate approved
                        approved_animals_pool.pop(idx)
                        break
                else:
                    return None
            else:
                animal = random.choice(animals)

            try:
                with transaction.atomic():
                    ad = Adoption.objects.create(
                        animal=animal,
                        adopter=adopter,
                        status=status,
                    )
                    # Adjust adoption_date to a random recent day
                    ad.adoption_date = random_date_within()
                    ad.save(update_fields=["adoption_date"])  # triggers model save logic again for dates only
            except Exception as e:
                # Skip conflicts (e.g., unique approved constraint) and continue
                self.stdout.write(self.style.WARNING(f"Skip: {e}"))
                return None

            if status == "approved":
                approved_created += 1
            elif status == "rejected":
                rejected_created += 1
            else:
                pending_created += 1
            return ad

        if per_user > 0:
            for user in adopters:
                for _ in range(per_user):
                    st = pick_status()
                    ad = create_one(user, st)
                    if ad:
                        created += 1
        else:
            for _ in range(count):
                user = random.choice(adopters)
                st = pick_status()
                ad = create_one(user, st)
                if ad:
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Adoções criadas: {created} (aprovadas: {approved_created}, pendentes: {pending_created}, rejeitadas: {rejected_created})"
            )
        )
