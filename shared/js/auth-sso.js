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

  // Parse hash parameters from window.location.hash
  function parseHashParams() {
    const hash = window.location.hash.startsWith('#') ? window.location.hash.substring(1) : window.location.hash;
    if (!hash) return null;

    const params = new URLSearchParams(hash);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      return { access_token: accessToken, refresh_token: refreshToken };
    }
    return null;
  }

  // Clean URL hash fragment seamlessly
  function cleanHashFragment() {
    if (window.history && window.history.replaceState) {
      const cleanUrl = window.location.pathname + window.location.search;
      window.history.replaceState(null, document.title, cleanUrl);
    } else {
      window.location.hash = '';
    }
  }

  // Handle SSO token restore from hash
  async function handleSSORestore() {
    const tokens = parseHashParams();
    if (!tokens) return;

    const client = getSupabaseClient();
    if (!client) {
      console.warn('[SSO] Supabase client not initialized; unable to set session from hash tokens.');
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
        cleanHashFragment();
      }
    } catch (err) {
      console.error('[SSO] Unexpected error setting session:', err);
    }
  }

  // Intercept click on ecosystem links to append session tokens
  function attachEcosystemLinkInterceptor() {
    document.addEventListener('click', async function (e) {
      const anchor = e.target.closest('a[href*="COSY"], a[href*="cosy"]');
      if (!anchor) return;

      const targetUrlStr = anchor.getAttribute('href');
      if (!targetUrlStr || targetUrlStr.startsWith('#') || targetUrlStr.startsWith('javascript:')) return;

      // Ensure link target points to an external/ecosystem page or subdomain
      try {
        const targetUrl = new URL(targetUrlStr, window.location.href);

        // Do not intercept relative links on same page unless domain matches external COSY domain
        const isExternalEcosystem = targetUrl.hostname !== window.location.hostname ||
                                    targetUrlStr.toLowerCase().includes('cosy');

        if (!isExternalEcosystem) return;

        const client = getSupabaseClient();
        if (!client) return;

        const { data } = await client.auth.getSession();
        const session = data?.session;

        if (session && session.access_token && session.refresh_token) {
          // Prevent default navigation briefly to append hash tokens
          e.preventDefault();

          targetUrl.hash = `access_token=${encodeURIComponent(session.access_token)}&refresh_token=${encodeURIComponent(session.refresh_token)}`;

          if (anchor.target === '_blank') {
            window.open(targetUrl.toString(), '_blank');
          } else {
            window.location.href = targetUrl.toString();
          }
        }
      } catch (err) {
        // If URL parsing fails, allow standard navigation
      }
    }, true);
  }

  // Initialize SSO on DOMContentLoaded or immediate if loaded later
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
