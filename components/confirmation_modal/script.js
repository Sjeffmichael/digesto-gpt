function confirmAction(element) {
    $confirmationButtom = document.getElementById(element.attributes['data-modal-target'].value).querySelector('#confirmation-button');
    $confirmationButtom.onclick = function(){ htmx.trigger(element, 'confirmed'); console.log('Action confirmed'); };
}

