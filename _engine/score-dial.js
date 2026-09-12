/**
 * ScoreDial Component
 * Compact score/points display that enlarges under data-context="projector".
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ScoreDial = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function ScoreDial(options) {
    options = options || {};
    this.score = typeof options.score === 'number' ? options.score : 0;
    this.label = options.label || 'Points';

    this.element = document.createElement('div');
    this.element.className = 'cg-score-dial';
    this.render();
  }

  ScoreDial.prototype.render = function () {
    this.element.innerHTML =
      '<div class="cg-score-label">' + escapeHtml(this.label) + '</div>' +
      '<div class="cg-score-value">' + this.score + '</div>';
  };

  ScoreDial.prototype.setScore = function (score) {
    this.score = score;
    this.render();
    if (this.element.classList) {
      this.element.classList.remove('motion-burst');
      // Trigger reflow to restart animation
      void this.element.offsetWidth;
      this.element.classList.add('motion-burst');
    }
  };

  ScoreDial.prototype.addScore = function (delta) {
    this.setScore(this.score + delta);
  };

  ScoreDial.prototype.appendTo = function (container) {
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

  return ScoreDial;
}));
