window.addEventListener('htmx:afterSwap', (event) => {

    // set the modal menu element
    const $targetEl = document.getElementById('user-data-modal');

    if ($targetEl !== null) {
        // options with default values
        const options = {
            placement: 'bottom-right',
            backdrop: 'dynamic',
            backdropClasses:
                'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-40',
            closable: true,
            onHide: () => {
                $targetEl.remove();
            },
        };

        // instance options object
        const instanceOptions = {
            id: 'user-data-modal',
            override: true
        };

        const modal = new Modal($targetEl, options, instanceOptions);

        const $closeBotton = document.getElementById('user-data-modal-close');

        $closeBotton.onclick = function(){ modal.hide(); };

        document.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.requestConfig.verb.toUpperCase() === 'PATCH') {
                modal.hide();
            }
        });

        modal.show();
    }

});
