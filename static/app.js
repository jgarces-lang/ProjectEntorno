document.addEventListener('DOMContentLoaded', function () {
  const grid = document.getElementById('product-grid');
  const catContainer = document.getElementById('category-filters');
  let allProducts = [];
  let categories = [];
  let activeCat = '';

  function formatPrice(n) {
    return n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function renderProducts(list) {
    if (list.length === 0) {
      grid.innerHTML = '<div class="empty-msg">No hay productos en esta categoría</div>';
      return;
    }
    grid.innerHTML = list.map(p => {
      const img = p.imagen_url
        ? `<img class="product-img" src="${p.imagen_url}" alt="${p.nombre}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=product-img-placeholder>📦</div>'">`
        : '<div class="product-img-placeholder">📦</div>';
      return `
        <div class="product-card">
          ${img}
          <div class="product-body">
            <div class="product-category">${p.categoria_nombre || 'Sin categoría'}</div>
            <div class="product-name">${p.nombre}</div>
            <div class="product-desc">${p.descripcion || 'Sin descripción'}</div>
            <div class="product-footer">
              <span class="product-price">${formatPrice(p.precio)}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  function filterProducts() {
    const filtered = activeCat
      ? allProducts.filter(p => p.categoria_id == activeCat)
      : allProducts;
    renderProducts(filtered);
  }

  function setupCategoryButtons() {
    catContainer.innerHTML = categories.map(c =>
      `<button class="cat-btn${activeCat == c.id ? ' active' : ''}" data-cat="${c.id}">${c.nombre}</button>`
    ).join('');

    catContainer.querySelectorAll('.cat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCat = btn.dataset.cat;
        filterProducts();
      });
    });

    document.querySelector('.cat-btn[data-cat=""]').addEventListener('click', () => {
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      document.querySelector('.cat-btn[data-cat=""]').classList.add('active');
      activeCat = '';
      filterProducts();
    });
  }

  async function loadData() {
    try {
      const [prodRes, catRes] = await Promise.all([
        fetch('/api/productos'),
        fetch('/api/categorias'),
      ]);
      if (!prodRes.ok || !catRes.ok) throw new Error('Error al cargar datos');
      allProducts = await prodRes.json();
      categories = await catRes.json();
      setupCategoryButtons();
      renderProducts(allProducts);
    } catch (err) {
      grid.innerHTML = `<div class="error-msg">Error al cargar productos: ${err.message}</div>`;
    }
  }

  loadData();
});
