// Onboarding — multi-step brand setup
document.addEventListener('DOMContentLoaded', () => {
  if (!localStorage.getItem('token')) {
    window.location.href = '/app/login.html';
    return;
  }

  const form = document.getElementById('onboarding-form');
  const steps = document.querySelectorAll('.step');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const submitBtn = document.getElementById('submit-btn');
  const stepContainers = document.querySelectorAll('.step-content');

  let currentStep = 0;

  function showStep(n) {
    stepContainers.forEach((el, i) => {
      el.style.display = i === n ? 'block' : 'none';
    });
    steps.forEach((el, i) => {
      el.className = 'step' + (i < n ? ' done' : '') + (i === n ? ' active' : '');
    });
    prevBtn.style.display = n === 0 ? 'none' : 'inline-flex';
    nextBtn.style.display = n === stepContainers.length - 1 ? 'none' : 'inline-flex';
    submitBtn.style.display = n === stepContainers.length - 1 ? 'inline-flex' : 'none';
  }

  prevBtn.addEventListener('click', () => { if (currentStep > 0) { currentStep--; showStep(currentStep); } });
  nextBtn.addEventListener('click', () => { if (currentStep < stepContainers.length - 1) { currentStep++; showStep(currentStep); } });

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
        img.style.cssText = 'width:80px;height:80px;border-radius:8px;object-fit:cover';
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  });

  // Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';

    const files = document.getElementById('images-input')?.files;
    const imageUrls = [];
    if (files) {
      for (const file of files) {
        imageUrls.push(URL.createObjectURL(file));
      }
    }

    try {
      await API.createBrand({
        name: document.getElementById('studio-name').value,
        industry: document.getElementById('industry').value,
        style: document.getElementById('style').value,
        tone: document.getElementById('tone').value,
        post_frequency: parseInt(document.getElementById('frequency').value),
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        image_urls: imageUrls,
      });

      // Trigger first generation
      await API.generate();
      window.location.href = '/app/dashboard.html';
    } catch (err) {
      showToast(err.message, 'error');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Done — Generate My Content';
    }
  });

  showStep(0);
});
