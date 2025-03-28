function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

    return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

function sendRequest(url, method, callback, body = null) {
    const options = {
        method: method,
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    fetch(url, options)
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => console.error(`Error: ${error}`));
}