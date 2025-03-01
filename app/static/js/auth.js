document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('#loginForm, #registerForm');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const username = form.querySelector('#username').value;
            const password = form.querySelector('#password').value;
            if (username.length < 3 || password.length < 6) {
                e.preventDefault();
                alert('Usuário deve ter pelo menos 3 caracteres e senha pelo menos 6.');
            }
        });
    });
});