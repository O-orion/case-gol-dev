document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const usernameHelp = document.getElementById('usernameHelp');
    const passwordHelp = document.getElementById('passwordHelp');
    const togglePassword = document.getElementById('togglePassword');

    // Validação em tempo real
    username.addEventListener('input', function () {
        if (username.value.length < 3) {
            usernameHelp.textContent = 'O usuário deve ter pelo menos 3 caracteres.';
            username.classList.add('is-invalid');
        } else {
            usernameHelp.textContent = '';
            username.classList.remove('is-invalid');
            username.classList.add('is-valid');
        }
    });

    password.addEventListener('input', function () {
        if (password.value.length < 6) {
            passwordHelp.textContent = 'A senha deve ter pelo menos 6 caracteres.';
            password.classList.add('is-invalid');
        } else {
            passwordHelp.textContent = '';
            password.classList.remove('is-invalid');
            password.classList.add('is-valid');
        }
    });

    // Validação no envio
    form.addEventListener('submit', function (event) {
        let isValid = true;

        if (username.value.length < 3) {
            usernameHelp.textContent = 'O usuário deve ter pelo menos 3 caracteres.';
            username.classList.add('is-invalid');
            isValid = false;
        }

        if (password.value.length < 6) {
            passwordHelp.textContent = 'A senha deve ter pelo menos 6 caracteres.';
            password.classList.add('is-invalid');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
        }

        form.classList.add('was-validated');
    });

    // Toggle de senha
    togglePassword.addEventListener('click', function () {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        const icon = this.querySelector('i');
        icon.classList.toggle('bi-eye');
        icon.classList.toggle('bi-eye-slash');
    });
});