document.getElementById('imageForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('file');
    const qualityInput = document.getElementById('quality');
    const resolutionInput = document.getElementById('resolution');

    for (const file of fileInput.files) {
        formData.append('files', file);
    }
    formData.append('quality', qualityInput.value);
    formData.append('resolution', resolutionInput.value);

    const response = await fetch('/compress', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = 'compressed_images.zip';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);

        document.getElementById('result').innerHTML = `
            <h2>Image compressed</h2>
            <a href="${url}" download="compressed_images.zip">Download Compressed Images</a>
        `;
    } else {
        document.getElementById('result').innerHTML = `<p class="error">Error compressing images.</p>`;
    }
});