/**
 * Novel Subscription JavaScript
 * Handles email subscription form validation and submission
 */

(function() {
  'use strict';

  // Google Apps Script URL (reused from blog)
  const SUBSCRIPTION_URL = 'https://script.google.com/macros/s/AKfycbwrz29kZAOs4a0jBYjpHlE6ehmHMPchhfF2zSck_aePLNfpgUFfikzqh74kytx0BOOs/exec';

  /**
   * Validate email address
   */
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email.toLowerCase());
  }

  /**
   * Show message to user
   */
  function showMessage(messageEl, message, type) {
    if (!messageEl) return;

    messageEl.textContent = message;
    messageEl.className = `subscription-message alert alert-${type}`;
    messageEl.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
      messageEl.style.display = 'none';
    }, 5000);
  }

  /**
   * Submit email to subscription service
   */
  async function subscribeUser(email, source) {
    try {
      const response = await fetch(SUBSCRIPTION_URL, {
        method: 'POST',
        mode: 'no-cors', // Required for Google Apps Script
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          source: source || 'novel-platform',
          timestamp: new Date().toISOString(),
          page: window.location.pathname
        })
      });

      // With no-cors mode, we can't read the response, so we assume success
      return { success: true };
    } catch (error) {
      console.error('Subscription error:', error);
      throw error;
    }
  }

  /**
   * Handle form submission
   */
  function handleFormSubmit(form, emailInput, messageEl, submitBtn) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      const email = emailInput.value.trim();
      const source = form.dataset.source || 'novel-platform';

      // Validate email
      if (!validateEmail(email)) {
        showMessage(messageEl, 'Please enter a valid email address.', 'danger');
        return;
      }

      // Disable button and show loading state
      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Subscribing...';

      try {
        await subscribeUser(email, source);

        // Show success message
        showMessage(messageEl, 'Success! Check your email to confirm your subscription.', 'success');

        // Reset form
        form.reset();

        // Track subscription (optional analytics)
        if (typeof gtag !== 'undefined') {
          gtag('event', 'subscribe', {
            event_category: 'Novel Platform',
            event_label: source
          });
        }
      } catch (error) {
        showMessage(messageEl, 'Oops! Something went wrong. Please try again.', 'danger');
      } finally {
        // Re-enable button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }

  /**
   * Initialize subscription forms
   */
  function initSubscriptionForms() {
    // Find all subscription forms on the page
    const forms = document.querySelectorAll('#novel-subscribe-form, .subscription-form');

    forms.forEach(form => {
      const emailInput = form.querySelector('input[type="email"]');
      const submitBtn = form.querySelector('button[type="submit"]');
      const messageEl = form.querySelector('.subscription-message') ||
                       form.parentElement.querySelector('.subscription-message') ||
                       document.getElementById('subscription-message');

      if (emailInput && submitBtn) {
        handleFormSubmit(form, emailInput, messageEl, submitBtn);
      }
    });
  }

  /**
   * Initialize when DOM is ready
   */
  function init() {
    initSubscriptionForms();
  }

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
