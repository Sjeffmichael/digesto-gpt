function togglePassword(element) {
    let password = element.closest("div").querySelector("input");
    const eyeIcon = element.querySelector('#eye');
    const eyeSlashIcon = element.querySelector('#eye-slash');

    if(password.type === "password") {
        password.type = "text";
        eyeIcon.classList.remove("hidden");
        eyeSlashIcon.classList.add("hidden");
    }
    else {
        password.type = "password";
        eyeIcon.classList.add("hidden");
        eyeSlashIcon.classList.remove("hidden");
    }
    // });
}
