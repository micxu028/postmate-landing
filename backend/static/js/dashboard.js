// Dashboard — preview & approve weekly content with smart empty states
document.addEventListener('DOMContentLoaded', async () => {
  if (!localStorage.getItem('token')) {
    window.location.href = '/app/login.html';
    return;
  }

  const grid = document.getElementById('post-grid');
  const weekNav = document.getElementById('week-label');
  const weekNavBar = document.getElementById('week-nav');
  const emptyState = document.getElementById('empty-state');
  const loadingState = document.getElementById('loading-state');
  const genState = document.getElementById('gen-state');
  const nbState = document.getElementById('nb-state');
  const generateBtn = document.getElementById('generate-btn');
  const genMessage = document.getElementById('gen-message');
  const ftBanner = document.getElementById('first-time-banner');

  let currentWeek = getWeekStart();

  // Show first-time banner if ?first=true
  if (new URLSearchParams(window.location.search).get('first') === 'true') {
    ftBanner.style.display = 'block';
    setTimeout(() => {
      ftBanner.style.display = 'none';
    }, 10000);
  }

  function getWeekStart(d) {
    const date = d ? new Date(d) : new Date();
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1);
    const monday = new Date(date.setDate(diff));
    return monday.toISOString().split('T')[0];
  }

  function formatWeekLabel(week) {
    const start = new Date(week + 'T00:00:00');
    const end = new Date(start);
    end.setDate(end.getDate() + 6);
    return `${start.toLocaleDateString('en-US', {month:'short', day:'numeric'})} – ${end.toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'})}`;
  }

  async function checkBrand() {
    try {
      await API.getBrand();
      return true;
    } catch (err) {
      return false;
    }
  }

  async function loadPosts() {
    grid.innerHTML = '';
    emptyState.style.display = 'none';
    genState.style.display = 'none';
    nbState.style.display = 'none';
    loadingState.style.display = 'block';
    weekNavBar.style.display = 'flex';
    weekNav.textContent = formatWeekLabel(currentWeek);

    try {
      // Check if brand exists
      const hasBrand = await checkBrand();
      if (!hasBrand) {
        loadingState.style.display = 'none';
        weekNavBar.style.display = 'none';
        nbState.style.display = 'block';
        return;
      }

      const data = await API.getPosts(currentWeek);
      loadingState.style.display = 'none';

      // Check if currently generating
      if (data.generating) {
        genState.style.display = 'block';
        startGenPolling();
        return;
      }

      if (!data.posts || data.posts.length === 0) {
        emptyState.style.display = 'block';
        return;
      }

      data.posts.sort((a, b) => a.day_of_week - b.day_of_week);
      renderPosts(data.posts);

    } catch (err) {
      loadingState.style.display = 'none';
      grid.innerHTML = `<div class="card" style="text-align:center;color:var(--red)">Error: ${err.message}</div>`;
    }
  }

  function renderPosts(posts) {
    posts.forEach(post => {
      const card = document.createElement('div');
      card.className = 'post-card';
      card.innerHTML = `
        <div class="img">
          ${post.image_url ? `<img src="${post.image_url}" alt="Post image">` : '<div class="spinner"></div>'}
        </div>
        <div class="body">
          <span class="badge badge-${post.status}">${post.status}</span>
          <p>${post.caption || 'No caption yet'}</p>
          <div class="tags">${post.hashtags?.join(' ') || ''}</div>
        </div>
        <div class="actions">
          <button class="btn btn-outline" data-action="reject" data-id="${post.id}">Regenerate</button>
          <button class="btn btn-primary" data-action="approve" data-id="${post.id}">Approve ✓</button>
        </div>
      `;
      grid.appendChild(card);
    });

    grid.querySelectorAll('[data-action="approve"]').forEach(btn => {
      btn.addEventListener('click', async () => {
        await API.approvePost(btn.dataset.id);
        showToast('Post approved!');
        loadPosts();
      });
    });
    grid.querySelectorAll('[data-action="reject"]').forEach(btn => {
      btn.addEventListener('click', async () => {
        await API.regeneratePost(btn.dataset.id);
        showToast('Marked for regeneration', 'error');
        loadPosts();
      });
    });
  }

  let genPollTimer = null;

  function startGenPolling() {
    if (genPollTimer) clearInterval(genPollTimer);
    genPollTimer = setInterval(async () => {
      try {
        const status = await API.generationStatus();
        if (genMessage) genMessage.textContent = status.message;
        if (status.stage === 'done' || status.stage === 'error') {
          clearInterval(genPollTimer);
          genPollTimer = null;
          loadPosts();
        }
      } catch (e) {
        // ignore
      }
    }, 2000);
  }

  // Week navigation
  document.getElementById('prev-week')?.addEventListener('click', () => {
    const d = new Date(currentWeek + 'T00:00:00');
    d.setDate(d.getDate() - 7);
    currentWeek = d.toISOString().split('T')[0];
    loadPosts();
  });
  document.getElementById('next-week')?.addEventListener('click', () => {
    const d = new Date(currentWeek + 'T00:00:00');
    d.setDate(d.getDate() + 7);
    currentWeek = d.toISOString().split('T')[0];
    loadPosts();
  });

  generateBtn?.addEventListener('click', async () => {
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    try {
      await API.generate();
      showToast('Generation started!');
      loadPosts();
    } catch (err) {
      showToast(err.message, 'error');
    }
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate This Week';
  });

  loadPosts();
});
