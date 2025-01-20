document.getElementById('convertForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const status = document.getElementById('status');
    const downloadButton = document.getElementById('downloadButton');
    const text = form.text.value;

    if (!text.trim()) {
        status.textContent = 'Please enter some text';
        return;
    }

    status.textContent = 'Converting...';
    downloadButton.style.display = 'none';

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                text: text
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            status.textContent = 'Conversion successful!';
            downloadButton.style.display = 'block';
        } else {
            throw new Error(data.message || 'Conversion failed');
        }
    } catch (error) {
        status.textContent = 'Error: ' + error.message;
        downloadButton.style.display = 'none';
    }
});

document.getElementById('downloadButton').addEventListener('click', async () => {
    const text = document.getElementById('textInput').value;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/download';
    
    const textInput = document.createElement('input');
    textInput.type = 'hidden';
    textInput.name = 'text';
    textInput.value = text;
    
    form.appendChild(textInput);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
});