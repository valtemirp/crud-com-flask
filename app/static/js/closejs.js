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
