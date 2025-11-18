// Pequeno toggle para o menu móvel.
// Incluir antes do </body> em templates (após incluir responsive.css).
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.querySelector('.mobile-nav-toggle');
    const menu = document.querySelector('.nav-menu');
    if (!toggle || !menu) return;
    toggle.addEventListener('click', function (e) {
        e.stopPropagation();
        menu.classList.toggle('show');
        toggle.classList.toggle('open');
    });
    // fechar menu ao clicar fora
    document.addEventListener('click', function (e) {
        if (!menu.classList.contains('show')) return;
        if (!menu.contains(e.target) && !toggle.contains(e.target)) {
            menu.classList.remove('show');
            toggle.classList.remove('open');
        }
    });
});