/**
 * shared/js/auth-guard.js
 *
 * Auth guard module for COSYmanuals.
 * Initializes Supabase JS client and verifies session authentication.
 * Unauthenticated users are redirected to COSYlanguages login page.
 */

(function () {
  const SUPABASE_URL = window.ENV_SUPABASE_URL || "https://your-supabase-project.supabase.co";
  const SUPABASE_ANON_KEY = window.ENV_SUPABASE_ANON_KEY || "your-anon-key";
  const LOGIN_URL = "https://cosylanguages.github.io/COSYlanguages/login.html";

  let client = null;

  if (typeof supabase !== 'undefined' && SUPABASE_URL && !SUPABASE_URL.includes("your-supabase-project")) {
    client = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }

  async function checkAuth(options = {}) {
    const { redirectOnFail = true, currentUrl = window.location.href } = options;

    if (!client) {
      console.warn("AuthGuard: Supabase client not initialized or offline.");
      if (redirectOnFail) {
        window.location.href = `${LOGIN_URL}?redirect=${encodeURIComponent(currentUrl)}`;
      }
      return { authenticated: false, session: null, error: "Supabase client not initialized" };
    }

    try {
      const { data, error } = await client.auth.getSession();
      if (error || !data || !data.session) {
        if (redirectOnFail) {
          window.location.href = `${LOGIN_URL}?redirect=${encodeURIComponent(currentUrl)}`;
        }
        return { authenticated: false, session: null, error: error ? error.message : "No active session" };
      }

      return { authenticated: true, session: data.session, error: null };
    } catch (err) {
      if (redirectOnFail) {
        window.location.href = `${LOGIN_URL}?redirect=${encodeURIComponent(currentUrl)}`;
      }
      return { authenticated: false, session: null, error: err.message };
    }
  }

  window.AuthGuard = {
    checkAuth,
    getClient: () => client,
    loginUrl: LOGIN_URL
  };
})();
