/******/ (() => { // webpackBootstrap
/*!*************************!*\
  !*** ./src/js/index.js ***!
  \*************************/
/*
 *  Copyright (c) 2021 Peter Christensen. All Rights Reserved.
 *  CC BY-NC-ND 4.0.
 */
function showPanel(panel, article) {
  panel.innerHTML = article.outerHTML;
  panel.classList.remove('hide');
  panel.classList.add('show');
}

function hidePanel(panel) {
  panel.classList.remove('show');
  panel.classList.add('hide');
}

document.querySelectorAll('.v-toggle').forEach((section) => {
  section.style.display = 'none';
});

window.addEventListener('load', function () {
  const panel = document.querySelector('#definition');
  document.addEventListener('click', (event) => {
    let exempt = false;
    if (
        event.target.localName === 'a'
        && event.target.classList.contains('unihan')) {
      exempt = true;
    } else if (event.target.closest('#definition')) {
      exempt = true;
    }
    if (!exempt) {
      hidePanel(panel);
    }
  });
  document.querySelectorAll('.unihan').forEach((link) => {
    link.onclick = (event) => {
      const article = document.querySelector(
        event.target.attributes.href.value
      );
      showPanel(panel, article)
      return false;
    }
  });
});

/******/ })()
;