// COSYlanguages Monolingual Grammar Manual Interactivity Engine
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mflip').forEach(card => {
    card.addEventListener('click', () => card.classList.toggle('revealed'));
  });

  document.querySelectorAll('.quiz-panel').forEach(panel => {
    let quizData = [];
    try { quizData = JSON.parse(panel.dataset.quiz || '[]'); } catch (e) { return; }
    const scoreEl = panel.querySelector('.quiz-score');
    const prefix = scoreEl ? scoreEl.textContent.replace(/0\s*\/.*$/, '') : '';
    let score = 0;
    function refreshScore() {
      if (scoreEl) scoreEl.textContent = prefix + score + ' / ' + quizData.length;
    }
    panel.querySelectorAll('.qitem').forEach((qitem, qidx) => {
      const opts = qitem.querySelectorAll('.qopt');
      const explain = qitem.querySelector('.qexplain');
      opts.forEach((opt, oidx) => {
        opt.addEventListener('click', () => {
          opts.forEach(o => { o.disabled = true; o.classList.remove('correct', 'wrong'); });
          if (oidx === quizData[qidx].correct) {
            opt.classList.add('correct');
            score++;
          } else {
            opt.classList.add('wrong');
            opts[quizData[qidx].correct].classList.add('correct');
          }
          refreshScore();
          if (explain) explain.style.display = 'block';
        });
      });
    });
    refreshScore();
    const resetBtn = panel.querySelector('.quiz-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        score = 0;
        panel.querySelectorAll('.qopt').forEach(o => { o.disabled = false; o.classList.remove('correct', 'wrong'); });
        panel.querySelectorAll('.qexplain').forEach(e => e.style.display = 'none');
        refreshScore();
      });
    }
  });
});
