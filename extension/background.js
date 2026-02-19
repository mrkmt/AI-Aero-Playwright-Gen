let recording = false;
let steps = [];


chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'START_RECORDING') {
        recording = true;
        steps = [];
        sendResponse({ status: 'started' });
    }


    if (msg.type === 'STOP_RECORDING') {
        recording = false;
        fetch('http://localhost:8000/api/v1/recorder/recording/steps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ steps })
        });
        sendResponse({ status: 'stopped', steps });
    }


    if (msg.type === 'ADD_STEP' && recording) {
        steps.push(msg.step);
    }
});