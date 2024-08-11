document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("auth-form");
    const suggestionForm = document.getElementById("suggestion-form");
    const loginError = document.getElementById("login-error");
    const loginDiv = document.getElementById("login-form");

    // Handle login form submission
    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const response = await fetch("/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            loginDiv.style.display = "none";
            suggestionForm.style.display = "block";
        } else {
            loginError.style.display = "block";
        }
    });


});

// Reference to the contenteditable div and suggestions div
const inputField = document.getElementById('text-input');
const suggestionsDiv = document.getElementById('suggestions');

// Function to add a <blank> placeholder into the contenteditable div
function addBlank() {
    const selection = window.getSelection();
    let range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

    // Check if the selection is within the contenteditable div
    if (!range || !inputField.contains(range.startContainer)) {
        // If the cursor is not in the inputField, place the blank at the end of the content
        inputField.focus();
        range = document.createRange();
        range.selectNodeContents(inputField);
        range.collapse(false); // Collapse the range to the end
    }

    const blankNode = document.createTextNode(" <blank> ");

    // Insert the <blank> text at the current cursor position or append at the end
    range.deleteContents();
    range.insertNode(blankNode);

    // Move the cursor to the end of the contenteditable div
    moveCursorToEnd(inputField);

    inputField.focus();
}

// Function to move the cursor to the end of the contenteditable div
function moveCursorToEnd(el) {
    const range = document.createRange();
    const selection = window.getSelection();
    range.selectNodeContents(el);
    range.collapse(false); // Collapse the range to the end
    selection.removeAllRanges();
    selection.addRange(range);
}

// Function to clear the contenteditable div and reset suggestions
function clearInput() {
    inputField.innerHTML = '';
    suggestionsDiv.innerHTML = '';
    inputField.setAttribute('data-placeholder', 'Type your sentence here...');
    moveCursorToEnd(inputField);
}

// Function to fetch suggestions from the server
function fetchSuggestions() {
    const text = inputField.innerText;

    // Simple validation to check if input includes <blank> surrounded by words
    const isValidFormat = /\b\w+\s*<blank>\s*\w+\b|\b\w+\s*<blank>\s*|\s*<blank>\s*\b\w+\b/.test(text);

    if (!isValidFormat) {
        suggestionsDiv.innerHTML = '<p class="loading">Please ensure the format is "word \< blank \> word".</p>';
        moveCursorToEnd(inputField);
        return;
    }

    suggestionsDiv.innerHTML = '<p class="loading">Loading suggestions...</p>';


    if (text.includes('<blank>')) {
        suggestionsDiv.innerHTML = '<p class="loading">Loading suggestions...</p>';

        fetch('/suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                text: text
            })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail); });
                }
                return response.json();
            })
            .then(data => {
                if (data.suggestions && data.suggestions.length > 0) {
                    const suggestionHTML = data.suggestions.map(suggestion =>
                        `<span onclick="replaceBlank('${suggestion}')">${suggestion}</span>`
                    ).join(', ');
                    suggestionsDiv.innerHTML = suggestionHTML;
                } else {
                    suggestionsDiv.innerHTML = '<p class="loading">No suggestions available.</p>';
                }
            })
            .catch(error => {
                suggestionsDiv.innerHTML = `<p class="loading">${error.message}</p>`;
            });
    } else {
        suggestionsDiv.innerHTML = '<p class="loading">Please add a blank to get suggestions.</p>';
    }
}

// Function to replace the <blank> with the clicked suggestion and highlight it
function replaceBlank(suggestion) {
    // Use a regular expression to replace the first occurrence of "<blank>"
    const htmlContent = inputField.innerHTML;
    const updatedContent = htmlContent.replace(/&lt;blank&gt;/, `<span class="highlighted">${suggestion}</span>`);
    inputField.innerHTML = updatedContent;

    // Optionally, you can reset the suggestions list after a selection
    suggestionsDiv.innerHTML = '';

    // Move the cursor to the end of the contenteditable div after replacement
    moveCursorToEnd(inputField);
}

// Fetch suggestions on input but prevent it from visually refreshing
inputField.addEventListener('input', (event) => {
    if (event.inputType !== 'insertText' || event.data !== ' ') {
        fetchSuggestions();
    }
});
