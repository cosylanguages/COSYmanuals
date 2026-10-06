/**
 * auth-sso.js - Ecosystem Cross-Domain Single Sign-On (SSO) Handler
 * COSYmanuals & COSY Ecosystem
 */

(function () {
  'use strict';

  // Helper to get or initialize Supabase client
  function getSupabaseClient() {
    if (window.supabaseClient) {
      return window.supabaseClient;
    }

    const supabaseUrl = window.ENV_SUPABASE_URL || window.SUPABASE_URL || "https://your-supabase-project.supabase.co";
    const supabaseAnonKey = window.ENV_SUPABASE_ANON_KEY || window.SUPABASE_ANON_KEY || "your-anon-key";

    if (typeof window.supabase !== 'undefined' && typeof window.supabase.createClient === 'function') {
      if (supabaseUrl && !supabaseUrl.includes("your-supabase-project")) {
        window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseAnonKey);
        return window.supabaseClient;
      }
    }
    return null;
  }

  // Parse session token parameters from location hash or search query params
  function parseSessionTokens() {
    let accessToken = null;
    let refreshToken = null;

    // Check hash parameters (#access_token=...&refresh_token=...)
    const hash = window.location.hash.startsWith('#') ? window.location.hash.substring(1) : window.location.hash;
    if (hash) {
      const hashParams = new URLSearchParams(hash);
      accessToken = hashParams.get('access_token');
      refreshToken = hashParams.get('refresh_token');
    }

    // Check query parameters (?access_token=...&refresh_token=...) if not in hash
    if (!accessToken || !refreshToken) {
      const searchParams = new URLSearchParams(window.location.search);
      if (!accessToken) accessToken = searchParams.get('access_token');
      if (!refreshToken) refreshToken = searchParams.get('refresh_token');
    }

    if (accessToken && refreshToken) {
      return { access_token: accessToken, refresh_token: refreshToken };
    }
    return null;
  }

  // Clean URL hash and query search params seamlessly without reloading
  function cleanURLParams() {
    if (window.history && window.history.replaceState) {
      const url = new URL(window.location.href);
      url.hash = '';
      url.searchParams.delete('access_token');
      url.searchParams.delete('refresh_token');
      window.history.replaceState(null, document.title, url.pathname + url.search);
    } else {
      window.location.hash = '';
    }
  }

  // Handle SSO token restore from URL
  async function handleSSORestore() {
    const tokens = parseSessionTokens();
    if (!tokens) return;

    const client = getSupabaseClient();
    if (!client) {
      console.warn('[SSO] Supabase client not initialized; unable to set session from SSO tokens.');
      return;
    }

    try {
      const { data, error } = await client.auth.setSession({
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token
      });

      if (error) {
        console.error('[SSO] Error setting session from SSO tokens:', error.message);
      } else {
        console.log('[SSO] Session restored successfully for user:', data?.user?.email || data?.session?.user?.id);
        cleanURLParams();
      }
    } catch (err) {
      console.error('[SSO] Unexpected error setting session:', err);
    }
  }

  // Intercept click on ecosystem links to append session transfer tokens
  function attachEcosystemLinkInterceptor() {
    document.addEventListener('click', function (e) {
      const anchor = e.target.closest('a[href*="COSY"], a[href*="cosy"], a[href*="github.io"]');
      if (!anchor) return;

      const targetUrlStr = anchor.getAttribute('href');
      if (!targetUrlStr || targetUrlStr.startsWith('#') || targetUrlStr.startsWith('javascript:')) return;

      try {
        const targetUrl = new URL(targetUrlStr, window.location.href);

        const lowerHref = targetUrlStr.toLowerCase();
        const lowerHost = targetUrl.hostname.toLowerCase();

        const isEcosystem = lowerHref.includes('cosy') ||
                            lowerHost.includes('cosy') ||
                            lowerHost.includes('github.io');

        if (!isEcosystem) return;

        const client = getSupabaseClient();
        if (!client) return;

        // Synchronously call e.preventDefault() before async operation
        e.preventDefault();

        // Perform async session retrieval and navigate
        (async function () {
          try {
            const { data } = await client.auth.getSession();
            const session = data?.session;

            if (session && session.access_token && session.refresh_token) {
              targetUrl.hash = `access_token=${encodeURIComponent(session.access_token)}&refresh_token=${encodeURIComponent(session.refresh_token)}`;
            }

            if (anchor.target === '_blank') {
              window.open(targetUrl.toString(), '_blank');
            } else {
              window.location.href = targetUrl.toString();
            }
          } catch (err) {
            // Fallback navigation if session check fails
            if (anchor.target === '_blank') {
              window.open(targetUrl.toString(), '_blank');
            } else {
              window.location.href = targetUrl.toString();
            }
          }
        })();
      } catch (err) {
        // Allow standard navigation if URL parsing fails
      }
    }, true);
  }

  // Initialize SSO on DOMContentLoaded or immediate execution
  function initSSO() {
    handleSSORestore();
    attachEcosystemLinkInterceptor();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSSO);
  } else {
    initSSO();
  }
})();
