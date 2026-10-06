/**
 * cms-editor.js - Founder Visual On-Page CMS Editor
 * COSYmanuals & COSY Ecosystem
 */

(function () {
  'use strict';

  let isEditMode = false;
  let originalContents = new Map();

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

  // Check if user has admin, founder, or owner role
  async function checkUserRole() {
    const client = getSupabaseClient();
    if (!client) return false;

    try {
      const { data } = await client.auth.getSession();
      const user = data?.session?.user;
      if (!user) return false;

      const role = (
        user.user_metadata?.role ||
        user.app_metadata?.role ||
        user.role ||
        window.COSY_USER?.role ||
        ''
      ).toLowerCase();

      return ['admin', 'founder', 'owner'].includes(role);
    } catch (err) {
      console.error('[CMS Editor] Error checking user role:', err);
      return false;
    }
  }

  // Get current page path key for cms_page_overrides
  function getPageKey() {
    return window.location.pathname || '/';
  }

  // Fetch live page content overrides from Supabase and apply to DOM
  async function loadPageOverrides() {
    const client = getSupabaseClient();
    if (!client) return;

    const pagePath = getPageKey();

    try {
      const { data, error } = await client
        .from('cms_page_overrides')
        .select('*')
        .eq('page_path', pagePath);

      if (error) {
        console.warn('[CMS Editor] Could not fetch page overrides:', error.message);
        return;
      }

      if (data && data.length > 0) {
        data.forEach(override => {
          if (override.element_id) {
            const el = document.getElementById(override.element_id);
            if (el && override.content_html) {
              el.innerHTML = override.content_html;
            }
          } else if (override.selector) {
            const el = document.querySelector(override.selector);
            if (el && override.content_html) {
              el.innerHTML = override.content_html;
            }
          }
        });
      }
    } catch (err) {
      console.error('[CMS Editor] Error applying overrides:', err);
    }
  }

  // Inject styles for the Founder CMS floating toolbar
  function injectCMSStyles() {
    const style = document.createElement('style');
    style.id = 'founder-cms-styles';
    style.textContent = `
      #founder-cms-toolbar {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        background: #1a202c;
        color: #fff;
        padding: 10px 16px;
        border-radius: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        border: 1px solid #2d3748;
      }
      #founder-cms-toolbar button {
        background: #6b202b;
        color: #ffffff;
        border: none;
        padding: 6px 14px;
        border-radius: 16px;
        cursor: pointer;
        font-weight: 600;
        font-size: 13px;
        transition: background 0.2s ease, transform 0.1s ease;
      }
      #founder-cms-toolbar button:hover {
        background: #8b2938;
        transform: translateY(-1px);
      }
      #founder-cms-toolbar button.active {
        background: #2b6cb0;
      }
      #founder-cms-status {
        font-size: 12px;
        color: #cbd5e0;
      }
      .cms-editable-active {
        outline: 2px dashed #3182ce !important;
        outline-offset: 4px;
        cursor: text;
      }
    `;
    document.head.appendChild(style);
  }

  // Render the floating Founder CMS toolbar
  function renderCMSToolbar() {
    if (document.getElementById('founder-cms-toolbar')) return;

    injectCMSStyles();

    const toolbar = document.createElement('div');
    toolbar.id = 'founder-cms-toolbar';
    toolbar.innerHTML = `
      <span style="font-weight: bold; color: #f7fafc;">👑 Founder CMS</span>
      <button id="cms-btn-edit">✏️ Edit Page Content</button>
      <button id="cms-btn-save" style="display: none;">💾 Save & Publish Live</button>
      <span id="cms-status-msg" id="founder-cms-status"></span>
    `;

    document.body.appendChild(toolbar);

    document.getElementById('cms-btn-edit').addEventListener('click', toggleEditMode);
    document.getElementById('cms-btn-save').addEventListener('click', saveAndPublish);
  }

  // Get editable targets on the page
  function getEditableElements() {
    // Target common content containers or explicit data-cms-editable elements
    const explicit = Array.from(document.querySelectorAll('[data-cms-editable]'));
    if (explicit.length > 0) return explicit;

    // Fallback to main sections, headings, paragraphs, notice bodies
    return Array.from(document.querySelectorAll(
      'main h1, main h2, main h3, main p, .notice-title, .notice-body, .section-subtitle, [id]'
    )).filter(el => !el.closest('#founder-cms-toolbar') && !el.closest('script'));
  }

  // Toggle inline visual editing mode
  function toggleEditMode() {
    isEditMode = !isEditMode;
    const editBtn = document.getElementById('cms-btn-edit');
    const saveBtn = document.getElementById('cms-btn-save');
    const editables = getEditableElements();

    if (isEditMode) {
      editBtn.textContent = '❌ Cancel Editing';
      editBtn.classList.add('active');
      saveBtn.style.display = 'inline-block';

      editables.forEach(el => {
        if (!el.id) {
          el.id = 'cms-el-' + Math.random().toString(36).substring(2, 9);
        }
        originalContents.set(el.id, el.innerHTML);
        el.setAttribute('contenteditable', 'true');
        el.classList.add('cms-editable-active');
      });
    } else {
      editBtn.textContent = '✏️ Edit Page Content';
      editBtn.classList.remove('active');
      saveBtn.style.display = 'none';

      editables.forEach(el => {
        el.removeAttribute('contenteditable');
        el.classList.remove('cms-editable-active');
      });
    }
  }

  // Save edits and upsert to Supabase cms_page_overrides
  async function saveAndPublish() {
    const client = getSupabaseClient();
    if (!client) {
      alert('Supabase client is not initialized.');
      return;
    }

    const statusMsg = document.getElementById('cms-status-msg');
    statusMsg.textContent = 'Saving...';

    const pagePath = getPageKey();
    const editables = getEditableElements();
    const overrides = [];

    editables.forEach(el => {
      if (el.id) {
        overrides.push({
          page_path: pagePath,
          element_id: el.id,
          content_html: el.innerHTML,
          updated_at: new Date().toISOString()
        });
      }
    });

    try {
      const { error } = await client
        .from('cms_page_overrides')
        .upsert(overrides, { onConflict: 'page_path,element_id' });

      if (error) {
        console.error('[CMS Editor] Error saving overrides:', error);
        statusMsg.textContent = '❌ Save failed!';
      } else {
        statusMsg.textContent = '✅ Saved & Published Live!';
        setTimeout(() => {
          statusMsg.textContent = '';
        }, 3000);
        toggleEditMode();
      }
    } catch (err) {
      console.error('[CMS Editor] Unexpected error during save:', err);
      statusMsg.textContent = '❌ Save error!';
    }
  }

  // Initialize CMS Editor
  async function initCMSEditor() {
    await loadPageOverrides();
    const isAuthorized = await checkUserRole();
    if (isAuthorized) {
      renderCMSToolbar();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCMSEditor);
  } else {
    initCMSEditor();
  }
})();
