// Onboarding — 2-step brand setup with live preview
document.addEventListener('DOMContentLoaded', () => {
  if (!localStorage.getItem('token')) {
    window.location.href = '/app/login.html';
    return;
  }

  const form = document.getElementById('onboarding-form');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const submitBtn = document.getElementById('submit-btn');
  const stepContainers = document.querySelectorAll('.step-content');
  const progressBar = document.getElementById('progress-bar');

  let currentStep = 0;

  // Card select
  document.querySelectorAll('.card-option').forEach(card => {
    card.addEventListener('click', () => {
      const parent = card.parentElement;
      parent.querySelectorAll('.card-option').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
  });

  // Frequency slider
  const freqSlider = document.getElementById('frequency');
  const freqDisplay = document.getElementById('freq-display');
  const freqSub = document.getElementById('freq-sub');
  if (freqSlider) {
    freqSlider.addEventListener('input', () => {
      const val = freqSlider.value;
      freqDisplay.textContent = val;
      freqSub.textContent = `~${Math.round(val * 4.3)} posts/month`;
    });
  }

  // Image preview
  document.getElementById('images-input')?.addEventListener('change', (e) => {
    const preview = document.getElementById('image-previews');
    preview.innerHTML = '';
    Array.from(e.target.files).forEach(file => {
      if (file.size > 5 * 1024 * 1024) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const img = document.createElement('img');
        img.src = ev.target.result;
        img.style.cssText = 'width:72px;height:72px;border-radius:8px;object-fit:cover';
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  });

  // Live preview updates
  function updatePreview() {
    const name = document.getElementById('studio-name').value || 'Your Studio';
    const city = document.getElementById('city').value || '';
    const state = document.getElementById('state').value || '';
    const industry = document.getElementById('industry');
    const industryLabel = industry ? industry.options[industry.selectedIndex]?.text?.split(' ')[0] || 'Yoga' : 'Yoga';

    document.getElementById('preview-name').textContent = name;
    document.getElementById('preview-location').textContent = [city, state].filter(Boolean).join(', ') || 'Location';
    document.getElementById('preview-industry').textContent = industryLabel;
  }

  document.getElementById('studio-name')?.addEventListener('input', updatePreview);
  document.getElementById('city')?.addEventListener('input', updatePreview);
  document.getElementById('state')?.addEventListener('input', updatePreview);
  document.getElementById('industry')?.addEventListener('change', updatePreview);

  function showStep(n) {
    stepContainers.forEach((el, i) => {
      el.style.display = i === n ? 'block' : 'none';
    });
    const pct = ((n + 1) / stepContainers.length) * 100;
    progressBar.style.width = pct + '%';

    prevBtn.style.display = n === 0 ? 'none' : 'inline-flex';
    nextBtn.style.display = n === stepContainers.length - 1 ? 'none' : 'inline-flex';
    submitBtn.style.display = n === stepContainers.length - 1 ? 'inline-flex' : 'none';
  }

  // Validation before proceeding
  function validateStep(n) {
    if (n === 0) {
      const name = document.getElementById('studio-name').value.trim();
      if (!name) { showToast('Please enter your business name', 'error'); return false; }
    }
    return true;
  }

  prevBtn.addEventListener('click', () => {
    if (currentStep > 0) { currentStep--; showStep(currentStep); }
  });

  nextBtn.addEventListener('click', () => {
    if (validateStep(currentStep) && currentStep < stepContainers.length - 1) {
      currentStep++; showStep(currentStep);
    }
  });

  // Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Setting up...';

    // Get card-select values
    const styleEl = document.querySelector('#style-select .card-option.selected');
    const toneEl = document.querySelector('#tone-select .card-option.selected');

    const files = document.getElementById('images-input')?.files;
    const imageUrls = [];
    if (files) {
      for (const file of files) {
        try {
          const formData = new FormData();
          formData.append('file', file);
          const res = await fetch('/api/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData,
          });
          const data = await res.json();
          if (res.ok) imageUrls.push(data.url);
        } catch (err) {
          console.warn('Upload failed, continuing:', err);
        }
      }
    }

    try {
      await API.createBrand({
        name: document.getElementById('studio-name').value.trim(),
        industry: document.getElementById('industry').value,
        style: styleEl ? styleEl.dataset.value : 'warm',
        tone: toneEl ? toneEl.dataset.value : 'friendly',
        post_frequency: parseInt(document.getElementById('frequency').value),
        city: document.getElementById('city').value.trim(),
        state: document.getElementById('state').value.trim(),
        image_urls: imageUrls,
      });

      // Go to generation progress page
      window.location.href = '/app/generating.html';
    } catch (err) {
      showToast(err.message, 'error');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Generate My Content →';
    }
  });

  // Select defaults
  document.querySelector('#style-select .card-option[data-value="warm"]')?.classList.add('selected');
  document.querySelector('#tone-select .card-option[data-value="friendly"]')?.classList.add('selected');

  showStep(0);
  updatePreview();
});
