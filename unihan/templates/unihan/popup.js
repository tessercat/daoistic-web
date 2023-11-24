function showPanel(event, panel) {
  const article = document.querySelector(event.target.attributes.href.value);
  panel.innerHTML = article.outerHTML;
  panel.classList.remove('hide');
  panel.classList.add('show');
}

function hidePanel(panel) {
  panel.classList.add('hide');
  panel.classList.remove('show');
}

function showCharacters(event) {
  const selector = `a.unihan.${event.target.text}`;
  document.querySelectorAll(selector).forEach((link) => {
    link.classList.add('highlight');
  });
}

function hideCharacters() {
  document.querySelectorAll('a.unihan.highlight').forEach((link) => {
    link.classList.remove('highlight');
  });
}

function initDefinitionPopup() {
  const panel = document.querySelector('#definition');

  // Hide the panel when the document scrolls.
  document.addEventListener('scroll', () => {
    hidePanel(panel);
  });

  // Hide the panel when the escape key is pressed.
  document.addEventListener('keydown', (event) => {
    if (event.key === "Escape") {
      if (panel.classList.contains('show')) {
        hidePanel(panel);
      } else {
        hideCharacters();
      }
    }
  });

  // Hide the panel and characters when the document is clicked,
  // unless the click is on a character link or on the panel itself.
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
      hideCharacters();
    }
  });

  // Show panel and characters when a Unihan character is clicked.
  document.querySelectorAll('a.unihan').forEach((link) => {
    link.addEventListener('click', (event) => {
      hideCharacters();
      showCharacters(event);
      showPanel(event, panel);
      event.preventDefault();
    });
  });

  console.log(
    `[daoistic ${new Date().toLocaleTimeString()}]`,
    'Definition popup enabled'
  );
}

function resetAll(event) {
  const output = document.querySelector('#output');
  output.innerHTML = '';
  output.innerText = '';
  const textarea = document.querySelector('#id_field');
  textarea.innerHTML = '';
  textarea.focus();
}

function initResetInput() {
  const reset = document.querySelector('#reset');
  reset.removeAttribute('disabled');
  reset.addEventListener('click', (event) => {
      resetAll(event);
  });
}

document.querySelectorAll('.js-hidden').forEach((element) => {
  element.style.display = 'none';
});
initDefinitionPopup();
initResetInput();
