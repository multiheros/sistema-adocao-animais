// Simple image preview for Animal form
document.addEventListener('DOMContentLoaded', () => {
	const fileInput = document.querySelector('input[type="file"][name="image"]');
	const preview = document.getElementById('image-preview');
	if (!fileInput || !preview) return;
	fileInput.addEventListener('change', () => {
		const [file] = fileInput.files || [];
		if (!file) {
			preview.innerHTML = '';
			return;
		}
		const img = document.createElement('img');
		img.className = 'img-fluid rounded border';
		img.alt = 'Pré-visualização da imagem';
		img.style.maxHeight = '240px';
		preview.innerHTML = '';
		preview.appendChild(img);
		const reader = new FileReader();
		reader.onload = e => { img.src = e.target.result; };
		reader.readAsDataURL(file);
	});
});