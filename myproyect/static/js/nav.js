function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
  }

  // Cerrar el menú si se hace clic fuera de él
  document.addEventListener('click', function (event) {
    var sidebar = document.getElementById('sidebar');
    var toggleBtn = document.querySelector('.toggle-sidebar-btn');

    if (!sidebar.contains(event.target) && !toggleBtn.contains(event.target)) {
      sidebar.classList.remove('show');
    }
  });

  // Funcionalidad para mostrar/ocultar el dropdown de usuario al hacer clic en la tarjeta
  document.getElementById('userCard').addEventListener('click', function (event) {
      const dropdown = document.querySelector('.user-dropdown');
      dropdown.classList.toggle('show');
  });

  // Cerrar el dropdown al hacer clic fuera
  document.addEventListener('click', function (event) {
      const dropdown = document.querySelector('.user-dropdown');
      if (!event.target.closest('#userCard') && dropdown.classList.contains('show')) {
          dropdown.classList.remove('show');
      }
  });