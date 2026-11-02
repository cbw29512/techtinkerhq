/* State: no choice, accepted, or declined. Only accepted loads gtag.js.
 * No request goes to Google Analytics before the visitor opts in.
 */
(() => {
  'use strict';

  const KEY = 'tthq_ga4_consent_v1';
  const loader = document.currentScript;
  const measurementId = loader ? loader.getAttribute('data-ga4-id') : '';
  let tagLoaded = false;

  function readChoice() {
    try {
      return window.localStorage.getItem(KEY);
    } catch (error) {
      console.warn('Could not read analytics preference', error);
      return null;
    }
  }

  function storeChoice(choice) {
    try {
      window.localStorage.setItem(KEY, choice);
    } catch (error) {
      console.warn('Could not persist analytics preference', error);
    }
  }

  function clearAnalyticsCookies() {
    try {
      document.cookie.split(';').forEach((entry) => {
        const name = entry.trim().split('=')[0];
        if (/^(_ga(?:_|$)|_gid$|_gat(?:_|$))/.test(name)) {
          document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax';
          document.cookie = name + '=; Max-Age=0; path=/; domain=' +
            location.hostname + '; SameSite=Lax';
        }
      });
    } catch (error) {
      console.warn('Could not clear all analytics cookies', error);
    }
  }

  function startAnalytics() {
    if (tagLoaded) return;
    if (!/^G-[A-Z0-9]+$/.test(measurementId || '')) {
      console.error('Invalid public GA4 measurement ID');
      return;
    }
    try {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('consent', 'default', {
        analytics_storage: 'denied', ad_storage: 'denied',
        ad_user_data: 'denied', ad_personalization: 'denied'
      });
      window.gtag('consent', 'update', { analytics_storage: 'granted' });
      window.gtag('js', new Date());
      window.gtag('config', measurementId, {
        allow_google_signals: false, allow_ad_personalization_signals: false
      });
      const remote = document.createElement('script');
      remote.async = true;
      remote.src = 'https://www.googletagmanager.com/gtag/js?id=' +
        encodeURIComponent(measurementId);
      document.head.appendChild(remote);
      tagLoaded = true;
    } catch (error) {
      console.error('Could not start optional Google Analytics', error);
    }
  }

  function initialize() {
    try {
      const banner = document.getElementById('analytics-consent');
      const accept = document.getElementById('analytics-accept');
      const decline = document.getElementById('analytics-decline');
      const settings = document.getElementById('analytics-settings');
      if (!banner || !accept || !decline || !settings) {
        throw new Error('Missing consent elements');
      }
      const show = () => {
        banner.hidden = false;
        banner.focus();
      };
      const choice = readChoice();
      if (choice === 'accepted') {
        startAnalytics();
      } else if (choice !== 'declined') {
        show();
      }
      settings.addEventListener('click', show);
      accept.addEventListener('click', () => {
        storeChoice('accepted');
        banner.hidden = true;
        startAnalytics();
        settings.focus();
      });
      decline.addEventListener('click', () => {
        storeChoice('declined');
        banner.hidden = true;
        if (typeof window.gtag === 'function') {
          window.gtag('consent', 'update', { analytics_storage: 'denied' });
        }
        clearAnalyticsCookies();
        if (tagLoaded) {
          // Reload removes the already-loaded remote script after withdrawal.
          window.location.reload();
        } else {
          settings.focus();
        }
      });
    } catch (error) {
      console.error('Could not initialize optional analytics control', error);
    }
  }

  try {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initialize, { once: true });
    } else {
      initialize();
    }
  } catch (error) {
    console.error('Could not register analytics consent control', error);
  }
})();
