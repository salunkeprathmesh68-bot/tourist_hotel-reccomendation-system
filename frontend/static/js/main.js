/**
 * Smart Kolhapur Guide - Main JavaScript
 * Handles real-time search, category filtering, budget slider updates, and favorites toggling.
 */

document.addEventListener('DOMContentLoaded', () => {
  initLiveSearch();
  initCategoryFilters();
  initBudgetSliders();
  initQuickPromptPills();
});

/**
 * Real-time client-side destination search (no page reload)
 */
function initLiveSearch() {
  const searchInput = document.getElementById('heroSearchInput');
  const placesGrid = document.getElementById('placesGrid');
  const placesCountSpan = document.getElementById('visiblePlacesCount');

  if (!searchInput || !placesGrid) return;

  const cards = placesGrid.querySelectorAll('.place-card');

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    let visibleCount = 0;

    const activeCategoryBtn = document.querySelector('.category-btn.active');
    const activeCategory = activeCategoryBtn ? activeCategoryBtn.getAttribute('data-category') : 'all';

    cards.forEach(card => {
      const name = card.getAttribute('data-name') ? card.getAttribute('data-name').toLowerCase() : '';
      const category = card.getAttribute('data-category') ? card.getAttribute('data-category').toLowerCase() : '';
      const text = card.textContent.toLowerCase();

      const matchesCategory = (activeCategory === 'all' || category === activeCategory);
      const matchesQuery = (!query || name.includes(query) || text.includes(query));

      if (matchesCategory && matchesQuery) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (placesCountSpan) {
      placesCountSpan.textContent = visibleCount;
    }

    const noResultsMsg = document.getElementById('noPlacesFoundMsg');
    if (noResultsMsg) {
      noResultsMsg.style.display = (visibleCount === 0) ? 'block' : 'none';
    }
  });
}

/**
 * Category filter buttons
 */
function initCategoryFilters() {
  const categoryBtns = document.querySelectorAll('.category-btn');
  const placesGrid = document.getElementById('placesGrid');
  const searchInput = document.getElementById('heroSearchInput');
  const placesCountSpan = document.getElementById('visiblePlacesCount');

  if (!categoryBtns.length || !placesGrid) return;

  const cards = placesGrid.querySelectorAll('.place-card');

  categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      categoryBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const selectedCategory = btn.getAttribute('data-category');
      const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
      let visibleCount = 0;

      cards.forEach(card => {
        const cardCategory = card.getAttribute('data-category') ? card.getAttribute('data-category').toLowerCase() : '';
        const name = card.getAttribute('data-name') ? card.getAttribute('data-name').toLowerCase() : '';
        const text = card.textContent.toLowerCase();

        const matchesCategory = (selectedCategory === 'all' || cardCategory === selectedCategory);
        const matchesQuery = (!query || name.includes(query) || text.includes(query));

        if (matchesCategory && matchesQuery) {
          card.style.display = 'flex';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      if (placesCountSpan) {
        placesCountSpan.textContent = visibleCount;
      }

      const noResultsMsg = document.getElementById('noPlacesFoundMsg');
      if (noResultsMsg) {
        noResultsMsg.style.display = (visibleCount === 0) ? 'block' : 'none';
      }
    });
  });
}

/**
 * Hotel recommendation budget sliders synchronization
 */
function initBudgetSliders() {
  const budgetMinInput = document.getElementById('budgetMinInput');
  const budgetMaxInput = document.getElementById('budgetMaxInput');
  const budgetMinVal = document.getElementById('budgetMinVal');
  const budgetMaxVal = document.getElementById('budgetMaxVal');

  if (budgetMinInput && budgetMinVal) {
    budgetMinInput.addEventListener('input', () => {
      budgetMinVal.textContent = '₹' + budgetMinInput.value;
    });
  }

  if (budgetMaxInput && budgetMaxVal) {
    budgetMaxInput.addEventListener('input', () => {
      budgetMaxVal.textContent = '₹' + budgetMaxInput.value;
    });
  }
}

/**
 * Clickable quick search shortcut suggestion pills (no voice popup, direct instant search)
 */
function initQuickPromptPills() {
  const voiceChips = document.querySelectorAll('.voice-chip');
  voiceChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt') || chip.textContent.trim();
      const searchInput = document.getElementById('heroSearchInput');
      const placesGrid = document.getElementById('placesGrid');

      // 1. If it's hotel intent, direct to hotel finder
      if (prompt.toLowerCase().includes('hotel')) {
        let dest = prompt.replace(/recommend hotels near /i, '').replace(/hotels near /i, '').replace(/"/g, '').trim();
        window.location.href = `/hotels?destination=rankala-lake`;
        return;
      }

      // 2. If it's category filter intent (e.g. "Show temples")
      if (prompt.toLowerCase().includes('show temples')) {
        const catBtn = document.querySelector('.category-btn[data-category="religion"]');
        if (catBtn) catBtn.click();
        if (placesGrid) placesGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }

      // 3. Clean search destination name and perform instant live search
      let cleanText = prompt.replace(/^Tell me about /i, '')
                            .replace(/^Show /i, '')
                            .replace(/"/g, '')
                            .trim();

      // Reset category to 'all' to show all matches
      const allCatBtn = document.querySelector('.category-btn[data-category="all"]');
      if (allCatBtn && !allCatBtn.classList.contains('active')) {
        allCatBtn.click();
      }

      if (searchInput) {
        searchInput.value = cleanText;
        searchInput.dispatchEvent(new Event('input'));
        searchInput.focus();
      }

      if (placesGrid) {
        placesGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/**
 * AJAX Toggle Favorite (Bookmark / Unbookmark)
 */
async function toggleFavorite(itemId, itemType, btnElement, cardIdToRemove = null) {
  try {
    const response = await fetch('/api/favorites/toggle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({
        item_id: itemId,
        item_type: itemType
      })
    });

    if (response.status === 401) {
      // User is not logged in
      const willLogin = confirm("Please log in to save destinations and hotels to your favorites wishlist!\n\nWould you like to go to the Login page now?");
      if (willLogin) {
        window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
      }
      return;
    }

    if (response.ok) {
      const data = await response.json();

      const isSaved = typeof data.is_saved === 'boolean' ? data.is_saved : data.action === 'added';

      if (btnElement) {
        if (isSaved) {
          btnElement.classList.add('active');
          btnElement.title = "Remove from favorites";
        } else {
          btnElement.classList.remove('active');
          btnElement.title = "Save to favorites";
        }
      }

      // If on detail page, update detail text
      const detailFavText = document.getElementById('detailFavText');
      if (detailFavText) {
        detailFavText.textContent = isSaved ? "Saved in Favorites" : "Save to Favorites";
      }

      // If on /my-favorites page and unbookmarked, animate and remove card
      if (cardIdToRemove && !isSaved) {
        const cardElem = document.getElementById(cardIdToRemove);
        if (cardElem) {
          cardElem.style.transition = 'all 0.3s ease';
          cardElem.style.opacity = '0';
          cardElem.style.transform = 'scale(0.9)';
          setTimeout(() => {
            cardElem.remove();
          }, 300);
        }
      }

      showToast(data.message || (isSaved ? 'Saved to your favorites.' : 'Removed from your favorites.'), isSaved ? 'success' : 'info');
    }
  } catch (err) {
    console.error("Error toggling favorite:", err);
    showToast("Network error. Please try again.", "danger");
  }
}

/**
 * Toast feedback notification
 */
function showToast(message, type = 'success') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.style.position = 'fixed';
    toastContainer.style.bottom = '24px';
    toastContainer.style.left = '24px';
    toastContainer.style.zIndex = '9999';
    toastContainer.style.display = 'flex';
    toastContainer.style.flexDirection = 'column';
    toastContainer.style.gap = '8px';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.style.background = (type === 'success') ? '#2E7D32' : (type === 'danger' ? '#C62828' : '#333');
  toast.style.color = '#fff';
  toast.style.padding = '10px 18px';
  toast.style.borderRadius = '30px';
  toast.style.fontSize = '0.88rem';
  toast.style.fontWeight = '500';
  toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.25)';
  toast.style.display = 'flex';
  toast.style.alignItems = 'center';
  toast.style.gap = '8px';
  toast.style.animation = 'slide-down 0.25s ease';

  const icon = (type === 'success') ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-info"></i>';
  toast.innerHTML = `${icon} <span>${message}</span>`;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 2800);
}
