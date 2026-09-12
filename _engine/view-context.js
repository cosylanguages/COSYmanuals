/**
 * ViewContext Helper
 * Sets document.documentElement.dataset.context to "projector", "phone", or "online".
 * Logic order:
 * 1. Manual override via URL param: ?data-context=projector|phone|online
 * 2. Online mode: ?mode=online or embedded inside an iframe (window.self !== window.top)
 * 3. Phone mode: viewport width < 480px
 * 4. Projector mode: default fallback
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ViewContext = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var ViewContext = {
    getContext: function () {
      var params = new URLSearchParams(window.location.search);

      // 1. Manual override via ?data-context=...
      var override = params.get('data-context');
      if (override && ['projector', 'phone', 'online'].indexOf(override.toLowerCase()) !== -1) {
        return override.toLowerCase();
      }

      // 2. Online mode
      var modeParam = params.get('mode');
      var isIframe = false;
      try {
        isIframe = window.self !== window.top;
      } catch (e) {
        isIframe = true;
      }
      if (modeParam === 'online' || isIframe) {
        return 'online';
      }

      // 3. Phone mode
      var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
      if (width < 480) {
        return 'phone';
      }

      // 4. Otherwise projector
      return 'projector';
    },

    updateContext: function () {
      var context = this.getContext();
      document.documentElement.dataset.context = context;
      return context;
    },

    init: function () {
      var self = this;
      self.updateContext();

      window.addEventListener('resize', function () {
        self.updateContext();
      });
    }
  };

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        ViewContext.init();
      });
    } else {
      ViewContext.init();
    }
  }

  return ViewContext;
}));
