function confirmAction(element) {
    $confirmationButtom = document.getElementById('confirmation-buttom');
    $confirmationButtom.onclick = function(){ htmx.trigger(element, 'confirmed'); }

}
