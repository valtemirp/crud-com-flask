document.addEventListener('DOMContentLoaded', function() {
    function closeAlert() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.querySelector('.close').addEventListener('click', function() {
                alert.style.display = 'none';
            });
        });
    }

    // Chame a função para fechar mensagens de alerta
    closeAlert();
});


document.querySelector('#titulo').addEventListener('input', function(e) {
    const value = e.target.value;
    const errorMessage = document.querySelector('#tituloError');

    if (value.length > 100) {
        errorMessage.textContent = 'O título não deve exceder 100 caracteres!';
    } else {
        errorMessage.textContent = '';
    }
});

document.querySelector('#ano').addEventListener('input', function(e) {
    const value = e.target.value;
    const errorMessage = document.querySelector('#anoError');

    if (value.length !== 4 || isNaN(value)) {
        errorMessage.textContent = 'Digite um ano válido com 4 dígitos.';
    } else {
        errorMessage.textContent = '';
    }
});

document.querySelector('#autor').addEventListener('input', function(e) {
    const value = e.target.value;
    const errorMessage = document.querySelector('#autorError');

    if (value.length > 100) {
        errorMessage.textContent = 'O nome do autor não deve exceder 100 caracteres!';
    } else {
        errorMessage.textContent = '';
    }
});
