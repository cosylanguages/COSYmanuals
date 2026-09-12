/**
 * BuzzerButton Component
 * A big single tap target with a pressed-state animation and haptic-style scale bounce.
 * No dependency on sound.
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.BuzzerButton = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function BuzzerButton(options) {
    options = options || {};
    this.label = options.label || 'BUZZ!';
    this.onBuzz = typeof options.onBuzz === 'function' ? options.onBuzz : null;

    this.element = document.createElement('button');
    this.element.type = 'button';
    this.element.className = 'cg-buzzer-button';
    this.element.textContent = this.label;

    this.bindEvents();
  }

  BuzzerButton.prototype.bindEvents = function () {
    var self = this;

    function triggerBuzz(e) {
      if (e) {
        e.preventDefault();
      }

      // Haptic feedback via Vibration API if supported by device
      if (typeof navigator !== 'undefined' && navigator.vibrate) {
        try {
          navigator.vibrate(50);
        } catch (err) {}
      }

      // Trigger scale bounce animation
      self.element.classList.remove('cg-haptic-bounce');
      void self.element.offsetWidth; // Reflow
      self.element.classList.add('cg-haptic-bounce');

      if (self.onBuzz) {
        self.onBuzz();
      }
    }

    this.element.addEventListener('pointerdown', function () {
      self.element.classList.add('is-pressed');
    });

    var clearPressed = function () {
      self.element.classList.remove('is-pressed');
    };

    this.element.addEventListener('pointerup', clearPressed);
    this.element.addEventListener('pointercancel', clearPressed);
    this.element.addEventListener('mouseleave', clearPressed);

    this.element.addEventListener('click', triggerBuzz);
  };

  BuzzerButton.prototype.appendTo = function (container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    if (container && container.appendChild) {
      container.appendChild(this.element);
    }
  };

  return BuzzerButton;
}));
