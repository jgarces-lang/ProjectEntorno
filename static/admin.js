document.addEventListener('DOMContentLoaded', function () {
  const loginScreen = document.getElementById('login-screen');
  const dashboard = document.getElementById('dashboard');
  const loginError = document.getElementById('login-error');
  const loginBtn = document.getElementById('login-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const adminUsername = document.getElementById('admin-username');
  const tableBody = document.getElementById('product-table-body');
  const productCount = document.getElementById('product-count');
  const addBtn = document.getElementById('add-product-btn');
  const modal = document.getElementById('product-modal');
  const modalTitle = document.getElementById('modal-title');
  const modalForm = document.getElementById('product-form');
  const modalCancel = document.getElementById('modal-cancel');
  const modalSave = document.getElementById('modal-save');
  const modalNombre = document.getElementById('modal-nombre');
  const modalPrecio = document.getElementById('modal-precio');
  const modalDesc = document.getElementById('modal-descripcion');
  const modalCat = document.getElementById('modal-categoria');
  const modalImagen = document.getElementById('modal-imagen');

  let token = null;
  let products = [];
  let categories = [];
  let editingId = null;

  function getAuthHeaders() {
    return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
  }

  function showLogin() {
    loginScreen.classList.remove('hidden');
    dashboard.classList.add('hidden');
  }

  function showDashboard() {
    loginScreen.classList.add('hidden');
    dashboard.classList.remove('hidden');
  }

  function loadState() {
    token = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_username');
    if (token && user) {
      adminUsername.textContent = user;
      showDashboard();
      loadProducts();
    }
  }

  loginBtn.addEventListener('click', async () => {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    loginError.textContent = '';
    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) { loginError.textContent = (await res.json()).detail || 'Error al ingresar'; return; }
      const data = await res.json();
      token = data.token;
      localStorage.setItem('admin_token', token);
      localStorage.setItem('admin_username', data.username);
      adminUsername.textContent = data.username;
      showDashboard();
      loadProducts();
    } catch { loginError.textContent = 'Error de red'; }
  });

  logoutBtn.addEventListener('click', () => {
    token = null;
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    showLogin();
  });

  async function loadProducts() {
    try {
      const [prodRes, catRes] = await Promise.all([
        fetch('/api/productos?solo_activos=false', { headers: { 'Authorization': `Bearer ${token}` } }).catch(() => fetch('/api/productos?solo_activos=false')),
        fetch('/api/categorias'),
      ]);
      products = await prodRes.json();
      categories = await catRes.json();
      renderTable();
      populateCategorySelect();
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--danger);padding:2rem;">Error: ${err.message}</td></tr>`;
    }
  }

  function populateCategorySelect(selectedId) {
    modalCat.innerHTML = '<option value="">Sin categoría</option>';
    categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.nombre;
      if (selectedId && c.id == selectedId) opt.selected = true;
      modalCat.appendChild(opt);
    });
  }

  function formatPrice(n) {
    return n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function renderTable() {
    if (products.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:2rem;">No hay productos aún</td></tr>';
      productCount.textContent = '0 productos';
      return;
    }
    productCount.textContent = `${products.length} producto(s)`;
    tableBody.innerHTML = products.map(p => {
      const catName = categories.find(c => c.id == p.categoria_id)?.nombre || '—';
      const badge = p.activo ? '<span class="badge active">Activo</span>' : '<span class="badge inactive">Inactivo</span>';
      return `
        <tr>
          <td>${p.id}</td>
          <td>${p.nombre}</td>
          <td>$${formatPrice(p.precio)}</td>
          <td>${catName}</td>
          <td>${badge}</td>
          <td class="td-actions">
            <button class="btn-sm edit" data-id="${p.id}">Editar</button>
            <button class="btn-sm toggle" data-id="${p.id}">${p.activo ? 'Desactivar' : 'Activar'}</button>
          </td>
        </tr>
      `;
    }).join('');

    tableBody.querySelectorAll('.btn-sm.edit').forEach(b => b.addEventListener('click', () => openEdit(b.dataset.id)));
    tableBody.querySelectorAll('.btn-sm.toggle').forEach(b => b.addEventListener('click', () => toggleProduct(b.dataset.id)));
  }

  function openModal(title, product) {
    modalTitle.textContent = title;
    modal.classList.remove('hidden');
    if (product) {
      editingId = product.id;
      modalNombre.value = product.nombre;
      modalPrecio.value = product.precio;
      modalDesc.value = product.descripcion || '';
      populateCategorySelect(product.categoria_id);
      modalImagen.value = product.imagen_url || '';
    } else {
      editingId = null;
      modalNombre.value = '';
      modalPrecio.value = '';
      modalDesc.value = '';
      populateCategorySelect();
      modalImagen.value = '';
    }
  }

  function closeModal() {
    modal.classList.add('hidden');
    editingId = null;
  }

  addBtn.addEventListener('click', () => openModal('Nuevo producto', null));
  modalCancel.addEventListener('click', closeModal);
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });

  modalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
      nombre: modalNombre.value.trim(),
      precio: parseFloat(modalPrecio.value),
      descripcion: modalDesc.value.trim(),
      categoria_id: modalCat.value ? parseInt(modalCat.value) : null,
      imagen_url: modalImagen.value.trim(),
    };

    try {
      let res;
      if (editingId) {
        res = await fetch(`/api/admin/productos/${editingId}`, {
          method: 'PUT',
          headers: getAuthHeaders(),
          body: JSON.stringify(body),
        });
      } else {
        res = await fetch('/api/admin/productos', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(body),
        });
      }
      if (!res.ok) { alert((await res.json()).detail || 'Error al guardar'); return; }
      closeModal();
      loadProducts();
    } catch (err) { alert('Error de red: ' + err.message); }
  });

  function openEdit(id) {
    const p = products.find(x => x.id == id);
    if (p) openModal('Editar producto', p);
  }

  async function toggleProduct(id) {
    const p = products.find(x => x.id == id);
    if (!p) return;
    try {
      const res = await fetch(`/api/admin/productos/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ activo: !p.activo }),
      });
      if (!res.ok) { alert((await res.json()).detail || 'Error'); return; }
      loadProducts();
    } catch (err) { alert('Error de red: ' + err.message); }
  }

  loadState();
});
