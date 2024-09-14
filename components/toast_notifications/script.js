window.addEventListener('htmx:oobAfterSwap', (event) => {
    var target = event.detail.target;
    target.querySelectorAll('.flex').forEach(element => {
        element.addEventListener('animationend', function(event) {
            if (event.animationName == 'toast-hide') {
                element.remove()
            }
        })
    });
})
