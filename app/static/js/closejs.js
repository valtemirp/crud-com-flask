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


// Inicialize a DataTable com as opções desejadas
$(document).ready(function () {
    $('.dataTable').DataTable({
        "ordering": true,  // Ativar ordenação nas colunas
        "lengthChange": false,  // Desativar opção de alterar o número de registros por página
        "pageLength": 10,  // Definir o número de registros por página
        "info": false,  // Ocultar informações de registros
        "language": {
            "paginate": {
                "previous": "Anterior",
                "next": "Próximo"
            },
            "search": "Buscar:"
        }
    });
});