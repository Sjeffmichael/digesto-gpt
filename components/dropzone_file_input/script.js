window.addEventListener('htmx:afterSwap', (event) => {
    $dropzoneFile = document.getElementById('dropzone-file');
    $fileInfo = document.getElementById('file-info');
    $removeFileButton = document.getElementById('remove-file');
    $dropzoneFileInput = document.getElementById('dropzone-file-input');

    $dropzoneFileInput.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dark:bg-gray-800', 'dark:border-gray-500');
    });

    $dropzoneFileInput.addEventListener('dragleave', function() {
        this.classList.remove('dark:bg-gray-800', 'dark:border-gray-500');
    });

    $dropzoneFileInput.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dark:bg-gray-800', 'dark:border-gray-500');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            var file = files[0];
            document.getElementById('file-name').textContent = file.name;
            $fileInfo.classList.remove('hidden');
        }
    });

    $dropzoneFile.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            var file = this.files[0];
            document.getElementById('file-name').textContent = file.name;
            $fileInfo.classList.remove('hidden');
        }
    });

    $removeFileButton.addEventListener('click', function(e) {
        e.preventDefault()
        $dropzoneFile.value = '';
        $fileInfo.classList.add('hidden');
    });
});
