// ===== Global State =====
let stockPrices = {};
let portfolio = [];

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    loadStocks();
    loadPortfolio();
    setupAutocomplete();
    setupPricePreview();
});

// ===== Background Particles =====
function createParticles() {
    const container = document.getElementById('bgParticles');
    const colors = [
        'rgba(99, 102, 241, 0.15)',
        'rgba(6, 182, 212, 0.12)',
        'rgba(139, 92, 246, 0.1)',
        'rgba(16, 185, 129, 0.08)',
    ];

    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.animationDuration = `${Math.random() * 15 + 10}s`;
        particle.style.animationDelay = `${Math.random() * 10}s`;
        container.appendChild(particle);
    }
}

// ===== API Calls =====
async function loadStocks() {
    try {
        const res = await fetch('/api/stocks');
        stockPrices = await res.json();
        renderStockChips();
    } catch (err) {
        showToast('Failed to load stocks', 'error');
    }
}

async function loadPortfolio() {
    try {
        const res = await fetch('/api/portfolio');
        const data = await res.json();
        portfolio = data.portfolio;
        updateUI(data);
    } catch (err) {
        showToast('Failed to load portfolio', 'error');
    }
}

async function addStock(e) {
    e.preventDefault();
    const stock = document.getElementById('stockInput').value.trim().toUpperCase();
    const quantity = parseInt(document.getElementById('quantityInput').value);

    if (!stock || !quantity || quantity <= 0) {
        showToast('Please enter a valid stock and quantity', 'error');
        return;
    }

    try {
        const res = await fetch('/api/portfolio/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stock, quantity })
        });

        const data = await res.json();

        if (res.ok) {
            portfolio = data.portfolio;
            updateUI(data);
            showToast(data.message, 'success');
            document.getElementById('addStockForm').reset();
            resetPreview();
            closeAutocomplete();
        } else {
            showToast(data.error, 'error');
        }
    } catch (err) {
        showToast('Failed to add stock', 'error');
    }
}

async function removeStock(stockName) {
    // Animate row removal first
    const rows = document.querySelectorAll('#portfolioBody tr');
    rows.forEach(row => {
        if (row.dataset.stock === stockName) {
            row.classList.add('row-removing');
        }
    });

    // Wait for animation then call API
    setTimeout(async () => {
        try {
            const res = await fetch('/api/portfolio/remove', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stock: stockName })
            });

            const data = await res.json();
            if (res.ok) {
                portfolio = data.portfolio;
                updateUI(data);
                showToast(data.message, 'info');
            }
        } catch (err) {
            showToast('Failed to remove stock', 'error');
        }
    }, 350);
}

async function clearPortfolio() {
    if (portfolio.length === 0) {
        showToast('Portfolio is already empty', 'info');
        return;
    }

    try {
        const res = await fetch('/api/portfolio/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await res.json();
        if (res.ok) {
            portfolio = data.portfolio;
            updateUI(data);
            showToast('Portfolio cleared', 'info');
        }
    } catch (err) {
        showToast('Failed to clear portfolio', 'error');
    }
}

function exportFile(format) {
    if (portfolio.length === 0) {
        showToast('Add stocks before exporting', 'error');
        return;
    }
    window.location.href = `/api/portfolio/export/${format}`;
    showToast(`Downloading .${format} file...`, 'success');
}

// ===== UI Update =====
function updateUI(data) {
    const { portfolio: items, total_investment } = data;

    // Update stats with animation
    animateValue('totalInvestment', `$${total_investment.toLocaleString('en-US', { minimumFractionDigits: 2 })}`);
    animateValue('totalHoldings', items.length.toString());
    animateValue('totalShares', items.reduce((sum, item) => sum + item.quantity, 0).toString());

    // Update table
    const tbody = document.getElementById('portfolioBody');
    const emptyState = document.getElementById('emptyState');
    const tableContainer = document.getElementById('tableContainer');

    if (items.length === 0) {
        emptyState.style.display = 'block';
        tableContainer.style.display = 'none';
        tbody.innerHTML = '';
    } else {
        emptyState.style.display = 'none';
        tableContainer.style.display = 'block';

        tbody.innerHTML = '';
        items.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.dataset.stock = item.stock;
            tr.style.animationDelay = `${index * 0.05}s`;
            tr.innerHTML = `
                <td>
                    <div class="stock-name">
                        <span class="stock-dot"></span>
                        ${item.stock}
                    </div>
                </td>
                <td class="stock-price-cell">$${item.price.toLocaleString()}</td>
                <td class="stock-qty-cell">${item.quantity}</td>
                <td class="stock-total-cell">$${item.total.toLocaleString()}</td>
                <td>
                    <button class="btn-danger-icon" onclick="removeStock('${item.stock}')" title="Remove ${item.stock}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function animateValue(elementId, newValue) {
    const el = document.getElementById(elementId);
    if (el.textContent !== newValue) {
        el.textContent = newValue;
        el.classList.remove('value-bump');
        // Trigger reflow
        void el.offsetWidth;
        el.classList.add('value-bump');
    }
}

// ===== Autocomplete =====
function setupAutocomplete() {
    const input = document.getElementById('stockInput');
    const dropdown = document.getElementById('autocompleteDropdown');

    input.addEventListener('input', () => {
        const val = input.value.trim().toUpperCase();
        if (!val) {
            closeAutocomplete();
            return;
        }

        const matches = Object.keys(stockPrices).filter(s => s.includes(val));
        if (matches.length === 0) {
            closeAutocomplete();
            return;
        }

        dropdown.innerHTML = '';
        matches.forEach(symbol => {
            const item = document.createElement('div');
            item.classList.add('autocomplete-item');
            item.innerHTML = `
                <span class="stock-symbol">${symbol}</span>
                <span class="stock-price">$${stockPrices[symbol]}</span>
            `;
            item.addEventListener('click', () => {
                input.value = symbol;
                closeAutocomplete();
                updatePreview();
                document.getElementById('quantityInput').focus();
            });
            dropdown.appendChild(item);
        });
        dropdown.style.display = 'block';
    });

    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.form-group')) {
            closeAutocomplete();
        }
    });
}

function closeAutocomplete() {
    document.getElementById('autocompleteDropdown').style.display = 'none';
}

// ===== Price Preview =====
function setupPricePreview() {
    const stockInput = document.getElementById('stockInput');
    const qtyInput = document.getElementById('quantityInput');

    stockInput.addEventListener('input', updatePreview);
    qtyInput.addEventListener('input', updatePreview);
}

function updatePreview() {
    const stock = document.getElementById('stockInput').value.trim().toUpperCase();
    const qty = parseInt(document.getElementById('quantityInput').value) || 0;
    const preview = document.getElementById('pricePreview');
    const previewVal = document.getElementById('previewValue');

    if (stockPrices[stock] && qty > 0) {
        const total = stockPrices[stock] * qty;
        previewVal.textContent = `$${total.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        preview.classList.add('active');
    } else {
        previewVal.textContent = '$0.00';
        preview.classList.remove('active');
    }
}

function resetPreview() {
    document.getElementById('previewValue').textContent = '$0.00';
    document.getElementById('pricePreview').classList.remove('active');
}

// ===== Stock Chips =====
function renderStockChips() {
    const container = document.getElementById('stockChips');
    container.innerHTML = '';

    Object.entries(stockPrices).forEach(([symbol, price]) => {
        const chip = document.createElement('div');
        chip.classList.add('stock-chip');
        chip.innerHTML = `${symbol} <span class="chip-price">$${price}</span>`;
        chip.addEventListener('click', () => {
            document.getElementById('stockInput').value = symbol;
            document.getElementById('quantityInput').focus();
            updatePreview();
            closeAutocomplete();
        });
        container.appendChild(chip);
    });
}

// ===== Toast Notifications =====
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.classList.add('toast', `toast-${type}`);

    const icons = {
        success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>',
        error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>',
        info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
    };

    toast.innerHTML = `${icons[type] || icons.info} <span>${message}</span>`;
    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
