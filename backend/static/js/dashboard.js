// Dashboard — preview & approve weekly content
document.addEventListener('DOMContentLoaded', async () => {
  if (!localStorage.getItem('token')) {
    window.location.href = '/app/login.html';
    return;
  }

  const grid = document.getElementById('post-grid');
  const weekNav = document.getElementById('week-label');
  const emptyState = document.getElementById('empty-state');
  const loadingState = document.getElementById('loading-state');
  const generateBtn = document.getElementById('generate-btn');

  let currentWeek = getWeekStart();

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

  async function loadPosts() {
    grid.innerHTML = '';
    emptyState.style.display = 'none';
    loadingState.style.display = 'block';
    weekNav.textContent = formatWeekLabel(currentWeek);

    try {
      const data = await API.getPosts(currentWeek);

      if (!data.posts || data.posts.length === 0) {
        loadingState.style.display = 'none';
        if (data.generating) {
          grid.innerHTML = '<div class="card" style="text-align:center"><div class="spinner"></div><p style="margin-top:16px">Generating your content...</p></div>';
          setTimeout(loadPosts, 5000);
        } else {
          emptyState.style.display = 'block';
        }
        return;
      }

      loadingState.style.display = 'none';
      data.posts.sort((a, b) => a.day_of_week - b.day_of_week);

      data.posts.forEach(post => {
        const card = document.createElement('div');
        card.className = 'post-card';
        card.innerHTML = `
          <div class="img">
            ${post.image_url ? `<img src="${post.image_url}" alt="Post image">` : '📷 Image generating...'}
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

      // Bind actions
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

    } catch (err) {
      loadingState.style.display = 'none';
      grid.innerHTML = `<div class="card" style="text-align:center;color:var(--red)">Error loading posts: ${err.message}</div>`;
    }
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
      setTimeout(loadPosts, 3000);
    } catch (err) {
      showToast(err.message, 'error');
    }
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Next Week';
  });

  loadPosts();
});
