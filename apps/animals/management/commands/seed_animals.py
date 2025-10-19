import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from apps.animals.models import Animal

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # Pillow should be installed, but keep graceful fallback
    Image = ImageDraw = ImageFont = None


ANIMALS_FIXTURES = [
    {"name": "Bolt", "species": "dog", "breed": "Vira-lata", "age": 3, "description": "Brincalhão e dócil."},
    {"name": "Luna", "species": "cat", "breed": "Siamês", "age": 2, "description": "Carinhosa e curiosa."},
    {"name": "Thor", "species": "dog", "breed": "Labrador", "age": 5, "description": "Companheiro e obediente."},
    {"name": "Mimi", "species": "cat", "breed": "Persa", "age": 4, "description": "Calma e dorminhoca."},
    {"name": "Piu", "species": "bird", "breed": "Calopsita", "age": 1, "description": "Canta ao amanhecer."},
    {"name": "Spike", "species": "reptile", "breed": "Iguana", "age": 2, "description": "Tranquilo e curioso."},
    {"name": "Nina", "species": "dog", "breed": "Poodle", "age": 6, "description": "Muito amigável com crianças."},
    {"name": "Zé", "species": "other", "breed": "Coelho", "age": 1, "description": "Gosta de cenouras."},
]


class Command(BaseCommand):
    help = "Popula a tabela de animais com dados de exemplo"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=len(ANIMALS_FIXTURES), help='Quantidade de registros para inserir (máx: fixtures)')
        parser.add_argument('--force', action='store_true', help='Inserir mesmo se já existem animais')
        parser.add_argument('--with-images', choices=['generate', 'download', 'none'], default='generate', help='Anexar imagens: generate (padrão), download ou none')

    def handle(self, *args, **options):
        count = options['count']
        force = options['force']
        with_images = options['with_images']

        if Animal.objects.exists() and not force:
            self.stdout.write(self.style.WARNING('Já existem animais no banco. Use --force para inserir mesmo assim.'))
            return

        created = 0
        images_set = 0
        media_animals_dir = os.path.join(settings.MEDIA_ROOT, 'animals')
        os.makedirs(media_animals_dir, exist_ok=True)

        for data in ANIMALS_FIXTURES[:count]:
            obj, was_created = Animal.objects.get_or_create(
                name=data['name'],
                defaults={
                    'species': data['species'],
                    'breed': data.get('breed', ''),
                    'age': data.get('age', 0),
                    'description': data.get('description', ''),
                    'adopted': False,
                }
            )
            if was_created:
                created += 1

            # Definir imagem se solicitado e o registro estiver sem imagem
            if with_images != 'none' and not obj.image:
                img_rel_path = f"animals/{slugify(data['name'])}.png"
                img_abs_path = os.path.join(settings.MEDIA_ROOT, img_rel_path)
                try:
                    if with_images == 'download':
                        self._download_or_generate_image(data, img_abs_path)
                    else:
                        self._generate_placeholder_image(data, img_abs_path)
                    # Salvar referência da imagem no model
                    obj.image.name = img_rel_path
                    obj.save(update_fields=['image'])
                    images_set += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Falha ao anexar imagem para {data['name']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Animais inseridos: {created} | Imagens definidas: {images_set}'))

    def _generate_placeholder_image(self, data, img_abs_path, size=(640, 400)):
        if Image is None:
            raise RuntimeError('Pillow não disponível para gerar imagens')
        colors = {
            'dog': '#2D6A4F',
            'cat': '#1D3557',
            'bird': '#B08968',
            'reptile': '#606C38',
            'other': '#6C757D',
        }
        bg = colors.get(data['species'], '#6C757D')
        name = data['name']
        species = data['species']
        img = Image.new('RGB', size, color=bg)
        draw = ImageDraw.Draw(img)
        # Fonte padrão do Pillow (monoespaçada)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        text = f"{name}\n{species.upper()}"
        # Centralizar texto (Pillow moderno usa multiline_textbbox)
        try:
            bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=6, align='center')
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            # Fallback para versões antigas
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size[0] - text_w) // 2
        y = (size[1] - text_h) // 2
        draw.multiline_text((x, y), text, fill='white', font=font, align='center', spacing=6)
        os.makedirs(os.path.dirname(img_abs_path), exist_ok=True)
        img.save(img_abs_path, format='PNG')

    def _download_or_generate_image(self, data, img_abs_path):
        """Tenta baixar uma imagem baseada na espécie; se falhar, gera placeholder."""
        try:
            import urllib.request
            urls_by_species = {
                'dog': 'https://placehold.co/640x400?text=Cachorro',
                'cat': 'https://placehold.co/640x400?text=Gato',
                'bird': 'https://placehold.co/640x400?text=Pássaro',
                'reptile': 'https://placehold.co/640x400?text=Réptil',
                'other': 'https://placehold.co/640x400?text=Animal',
            }
            url = urls_by_species.get(data['species'], urls_by_species['other'])
            os.makedirs(os.path.dirname(img_abs_path), exist_ok=True)
            urllib.request.urlretrieve(url, img_abs_path)
        except Exception:
            # Fallback para geração local
            self._generate_placeholder_image(data, img_abs_path)