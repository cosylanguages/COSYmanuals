/**
 * TurnBanner Component
 * Shows whose turn and who is next.
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.TurnBanner = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function TurnBanner(options) {
    options = options || {};
    this.activePlayer = options.activePlayer || 'Player 1';
    this.nextPlayer = options.nextPlayer || 'Player 2';

    this.element = document.createElement('div');
    this.element.className = 'cg-turn-banner';
    this.render();
  }

  TurnBanner.prototype.render = function () {
    this.element.innerHTML =
      '<div class="cg-turn-active">' +
        '<span>Turn:</span> ' +
        '<span class="cg-turn-active-name">' + escapeHtml(this.activePlayer) + '</span>' +
      '</div>' +
      '<div class="cg-turn-next">' +
        '<span>Next:</span> ' +
        '<span class="cg-turn-next-name">' + escapeHtml(this.nextPlayer) + '</span>' +
      '</div>';
  };

  TurnBanner.prototype.setTurn = function (activePlayer, nextPlayer) {
    this.activePlayer = activePlayer;
    if (nextPlayer !== undefined) {
      this.nextPlayer = nextPlayer;
    }
    this.render();
    if (this.element.classList) {
      this.element.classList.remove('motion-slide-chain');
      // Trigger reflow to restart animation
      void this.element.offsetWidth;
      this.element.classList.add('motion-slide-chain');
    }
  };

  TurnBanner.prototype.appendTo = function (container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    if (container && container.appendChild) {
      container.appendChild(this.element);
    }
  };

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  return TurnBanner;
}));
