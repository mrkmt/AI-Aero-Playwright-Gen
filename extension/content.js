function cssPath(el) {
    let path = [];
    while (el.nodeType === Node.ELEMENT_NODE) {
        let selector = el.nodeName.toLowerCase();
        if (el.id) {
            selector += '#' + el.id;
            path.unshift(selector);
            break;
        } else {
            let sib = el, nth = 1;
            while ((sib = sib.previousElementSibling)) nth++;
            selector += `:nth-child(${nth})`;
        }
        path.unshift(selector);
        el = el.parentNode;
    }
    return path.join(' > ');
}


function record(action, target, value = '') {
    chrome.runtime.sendMessage({
        type: 'ADD_STEP',
        step: {
            action_type: action,
            selector_snapshot: cssPath(target),
            tag: target.tagName,
            input_value_masked: value,
            url: location.href,
            timestamp: Date.now()
        }
    });
}


// CLICK
document.addEventListener('click', e => {
    record('click', e.target);
}, true);


// INPUT
document.addEventListener('input', e => {
    record('input', e.target, e.target.value);
}, true);


// CHANGE (dropdowns)
document.addEventListener('change', e => {
    record('change', e.target, e.target.value);
}, true);


// FORM SUBMIT
document.addEventListener('submit', e => {
    record('submit', e.target);
}, true);


// PAGE NAVIGATION
let lastUrl = location.href;
setInterval(() => {
    if (location.href !== lastUrl) {
        record('navigate', document.body, location.href);
        lastUrl = location.href;
    }
}, 500);