/**
 * Novel Reader JavaScript
 * Handles reading progress, bookmarks, keyboard navigation, and reading time estimation
 */

(function() {
  'use strict';

  /**
   * Update reading progress bar on scroll
   */
  function updateReadingProgress() {
    const progressBar = document.querySelector('.reading-progress');
    if (!progressBar) return;

    const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;

    progressBar.style.width = scrolled + '%';
  }

  /**
   * Save current scroll position to localStorage
   */
  function saveBookmark() {
    const novelId = document.body.dataset.novelId;
    const chapterId = document.body.dataset.chapterId;

    if (novelId && chapterId) {
      const scrollPosition = window.scrollY;
      localStorage.setItem(`novel_${novelId}_${chapterId}_scroll`, scrollPosition);
      localStorage.setItem(`novel_${novelId}_lastChapter`, chapterId);
      localStorage.setItem(`novel_${novelId}_lastVisit`, new Date().toISOString());
    }
  }

  /**
   * Restore saved scroll position from localStorage
   */
  function restoreBookmark() {
    const novelId = document.body.dataset.novelId;
    const chapterId = document.body.dataset.chapterId;

    if (novelId && chapterId) {
      const savedPosition = localStorage.getItem(`novel_${novelId}_${chapterId}_scroll`);

      if (savedPosition && parseInt(savedPosition) > 100) {
        setTimeout(() => {
          window.scrollTo({
            top: parseInt(savedPosition),
            behavior: 'smooth'
          });
          showNotification('Bookmark restored');
        }, 100);
      }
    }
  }

  /**
   * Show notification message
   */
  function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: var(--global-theme-color);
      color: white;
      padding: 12px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      z-index: 1000;
      font-size: 0.9rem;
      font-weight: 600;
      animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease';
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  }

  /**
   * Add CSS animations for notifications
   */
  function addNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideInRight {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      @keyframes slideOutRight {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Setup keyboard navigation for chapters
   */
  function setupKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
      // Prevent navigation if user is typing in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      // Left arrow - previous chapter
      if (e.key === 'ArrowLeft') {
        const prevBtn = document.querySelector('.nav-btn-prev');
        if (prevBtn && !prevBtn.classList.contains('disabled')) {
          window.location.href = prevBtn.href;
        }
      }

      // Right arrow - next chapter
      if (e.key === 'ArrowRight') {
        const nextBtn = document.querySelector('.nav-btn-next');
        if (nextBtn && !nextBtn.classList.contains('disabled')) {
          window.location.href = nextBtn.href;
        }
      }

      // Up arrow - all chapters
      if (e.key === 'ArrowUp' && e.ctrlKey) {
        const allBtn = document.querySelector('.nav-btn-all');
        if (allBtn) {
          window.location.href = allBtn.href;
        }
      }
    });
  }

  /**
   * Calculate and display reading time
   */
  function calculateReadingTime() {
    const content = document.querySelector('.chapter-content');
    if (!content) return;

    const text = content.innerText || content.textContent;
    const wordCount = text.trim().split(/\s+/).length;
    const wordsPerMinute = 250;
    const minutes = Math.ceil(wordCount / wordsPerMinute);

    const readingTimeElement = document.querySelector('.reading-time-display');
    if (readingTimeElement) {
      if (minutes < 60) {
        readingTimeElement.textContent = `${minutes} min read`;
      } else {
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        readingTimeElement.textContent = `${hours}h ${remainingMinutes}m read`;
      }
    }
  }

  /**
   * Mark new chapters (published < 7 days ago)
   */
  function markNewChapters() {
    const chapterCards = document.querySelectorAll('.chapter-card');
    const now = new Date();
    const sevenDaysAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);

    chapterCards.forEach(card => {
      const publishDate = card.dataset.publishDate;
      if (publishDate) {
        const cardDate = new Date(publishDate);
        if (cardDate > sevenDaysAgo) {
          const titleEl = card.querySelector('.chapter-title');
          if (titleEl && !card.querySelector('.badge-new')) {
            const badge = document.createElement('span');
            badge.className = 'badge-new';
            badge.innerHTML = ' NEW';
            titleEl.appendChild(badge);
          }
        }
      }
    });
  }

  /**
   * Initialize all reading features
   */
  function init() {
    addNotificationStyles();

    // Reading progress bar (only on chapter pages)
    if (document.querySelector('.reading-progress')) {
      window.addEventListener('scroll', updateReadingProgress);
      updateReadingProgress();
    }

    // Bookmarking (only on chapter pages)
    if (document.body.dataset.novelId && document.body.dataset.chapterId) {
      restoreBookmark();

      // Save bookmark on scroll (debounced)
      let scrollTimeout;
      window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(saveBookmark, 500);
      });

      // Save bookmark on page exit
      window.addEventListener('beforeunload', saveBookmark);
    }

    // Keyboard navigation
    setupKeyboardNavigation();

    // Reading time calculation
    calculateReadingTime();

    // Mark new chapters
    markNewChapters();
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
