/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./src/js/index.js":
/*!*************************!*\
  !*** ./src/js/index.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _logger_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./logger.js */ "./src/js/logger.js");
/*
 *  Copyright (c) 2021 Peter Christensen. All Rights Reserved.
 *  CC BY-NC-ND 4.0.
 */


function hidePanel(panel) {
  panel.classList.add('hide');
  panel.classList.remove('show');
}

function showPanel(event, panel) {
  // Load clicked-link data into the definition panel.
  const article = document.querySelector(event.target.attributes.href.value);
  panel.innerHTML = article.outerHTML;
  //logger.info('height', event.target.offsetHeight);
  //logger.info('left', event.target.offsetLeft);
  //logger.info('top', event.target.offsetTop);
  //logger.info('width', event.target.offsetWidth);
  panel.classList.remove('hide');
  panel.classList.add('show');
}

function addVocabListeners() {
  const panel = document.querySelector('#definition');

  // Hide the panel when the document scrolls.
  document.addEventListener('scroll', () => {
    hidePanel(panel);
  });

  // Hide the panel when the document is clicked, unless the click is on
  // a Unihan character link or on the panel itself.
  document.addEventListener('click', (event) => {
    if (panel.classList.contains('hide')) {
      return;
    }
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

  // Show the panel when a Unihan character is clicked.
  document.querySelectorAll('.unihan').forEach((link) => {
    link.addEventListener('click', (event) => {
      showPanel(event, panel);
      event.preventDefault();
    });
  });

  _logger_js__WEBPACK_IMPORTED_MODULE_0__.default.info('Vocab enabled.');
}

// Set log vars and hide vocab elements as soon as the script runs.
document.debugLogEnabled = true;
document.infoLogEnabled = true;
document.querySelectorAll('.v-toggle').forEach((section) => {
  section.style.display = 'none';
});

// Init the definitions panel when the page loads.
window.addEventListener('load', function() {
  addVocabListeners();
});


/***/ }),

/***/ "./src/js/logger.js":
/*!**************************!*\
  !*** ./src/js/logger.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => __WEBPACK_DEFAULT_EXPORT__
/* harmony export */ });
/*
 *  Copyright (c) 2021 Peter Christensen. All Rights Reserved.
 *  CC BY-NC-ND 4.0.
 */
function logPrefix() {
  return `[daoistic ${new Date().toLocaleTimeString()}]`;
}

let logger = {
  debug: (...args) => {
    if (document.debugLogEnabled) {
      console.debug(logPrefix(), ...args);
    }
  },
  info: (...args) => {
    if (document.infoLogEnabled) {
      console.log(logPrefix(), ...args);
    }
  },
  error: (...args) => {
    console.error(logPrefix(), ...args);
  }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (logger);


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		if(__webpack_module_cache__[moduleId]) {
/******/ 			return __webpack_module_cache__[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop)
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	// startup
/******/ 	// Load entry module
/******/ 	__webpack_require__("./src/js/index.js");
/******/ 	// This entry module used 'exports' so it can't be inlined
/******/ })()
;