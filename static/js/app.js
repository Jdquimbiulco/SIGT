/* ============================================================
   SIGT - Liceo Campo Verde
   Navegación ligera (SPA) + menú responsive
   ============================================================ */

(function () {
    'use strict';

    var contentBody = document.querySelector('.content-body');
    if (!contentBody) return;

    /* ---------- Botón "Volver": solo en páginas secundarias ---------- */
    var mainPaths = [];
    try {
        mainPaths = JSON.parse(document.body.getAttribute('data-main-paths') || '[]');
    } catch (e) { /* sin rutas: dejamos el botón visible */ }

    function actualizarVolver() {
        var btn = document.getElementById('btn-volver');
        if (!btn) return;
        var esPrincipal = mainPaths.indexOf(window.location.pathname) !== -1;
        btn.classList.toggle('d-none', esPrincipal);
    }
    actualizarVolver();

    /* ---------- Navegación ligera ---------- */
    if (window.history && typeof window.fetch === 'function') {

        function cargarSpa(url, desdePop) {
            return fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
                redirect: 'follow'
            }).then(function (resp) {
                var ct = resp.headers.get('content-type') || '';
                if (!resp.ok || resp.redirected || ct.indexOf('text/html') === -1) {
                    window.location.href = url;
                    return Promise.reject();
                }
                return resp.text();
            }).then(function (html) {
                var doc = new DOMParser().parseFromString(html, 'text/html');
                var nuevo = doc.querySelector('.content-body');
                if (!nuevo) {
                    window.location.href = url;
                    return;
                }
                var titulo = doc.querySelector('title');
                if (titulo) document.title = titulo.textContent;

                contentBody.innerHTML = nuevo.innerHTML;
                window.scrollTo(0, 0);

                doc.querySelectorAll('script').forEach(function (s) {
                    if (s.src) return;
                    try { new Function(s.textContent)(); } catch (e) { console.error(e); }
                });

                document.querySelectorAll('.sidebar .nav-link').forEach(function (a) {
                    a.classList.remove('active');
                    var objetivo = new URL(url, window.location.origin);
                    if (a.href === objetivo.href) a.classList.add('active');
                });

                if (!desdePop) {
                    history.pushState({ url: url }, '', url);
                }
                actualizarVolver();
                cerrarMenu();
            }).catch(function (err) {
                if (err) window.location.href = url;
            });
        }

        document.addEventListener('click', function (e) {
            var a = e.target.closest('a[href]');
            if (!a) return;
            if (a.target === '_blank' || a.hasAttribute('download') || a.hash) return;
            var href = a.getAttribute('href');
            if (!href || href.charAt(0) === '#' || href.indexOf('javascript:') === 0) return;
            var destino;
            try { destino = new URL(a.href, window.location.origin); }
            catch (err) { return; }
            if (destino.origin !== window.location.origin) return;
            if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
            if (a.getAttribute('data-bs-toggle')) return;
            e.preventDefault();
            cargarSpa(destino.href);
        });

        window.addEventListener('popstate', function (e) {
            actualizarVolver();
            var url = (e.state && e.state.url) || window.location.href;
            cargarSpa(url, true);
        });
    }

    /* ---------- Menú responsive (móvil) ---------- */
    var sidebar = document.getElementById('sidebar');
    if (!sidebar || typeof window.matchMedia !== 'function') return;

    var backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    backdrop.id = 'sidebar-backdrop';
    document.body.appendChild(backdrop);

    backdrop.addEventListener('click', cerrarMenu);

    window.toggleMenu = function () {
        if (sidebar.classList.contains('show')) {
            cerrarMenu();
        } else {
            abrirMenu();
        }
    };

    function abrirMenu() {
        sidebar.classList.add('show');
        backdrop.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function cerrarMenu() {
        sidebar.classList.remove('show');
        backdrop.classList.remove('show');
        document.body.style.overflow = '';
    }
})();