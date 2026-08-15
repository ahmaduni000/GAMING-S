/* ============================================
   GameZone Hub - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

    // === Flash Messages Auto-dismiss ===
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(function () { msg.remove(); }, 300);
        }, 4700);

        // Close button
        const closeBtn = msg.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                msg.style.animation = 'fadeOut 0.3s ease forwards';
                setTimeout(function () { msg.remove(); }, 300);
            });
        }
    });

    // === Scroll to Top Button ===
    const scrollTopBtn = document.querySelector('.scroll-top');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });

        scrollTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // === Cart Quantity Controls ===
    document.querySelectorAll('.qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = this.parentElement.querySelector('input[type="number"]');
            if (!input) return;
            let val = parseInt(input.value) || 1;
            if (this.classList.contains('qty-minus')) {
                val = Math.max(1, val - 1);
            } else {
                val = val + 1;
            }
            input.value = val;

            // Trigger change event for auto-update forms
            input.dispatchEvent(new Event('change'));
        });
    });

    // === Auto-submit quantity changes in cart ===
    document.querySelectorAll('.auto-submit').forEach(function (el) {
        el.addEventListener('change', function () {
            this.closest('form').submit();
        });
    });

    // === Product Image Gallery ===
    const mainImage = document.querySelector('.main-product-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    thumbnails.forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            if (mainImage) {
                mainImage.src = this.src;
            }
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // === Wishlist Toggle ===
    document.querySelectorAll('.wishlist-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.dataset.url || this.href;
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const icon = this.querySelector('i');
                        if (data.wishlisted) {
                            icon.classList.remove('far');
                            icon.classList.add('fas');
                            icon.style.color = '#ef4444';
                            showToast('Added to wishlist!', 'success');
                        } else {
                            icon.classList.remove('fas');
                            icon.classList.add('far');
                            icon.style.color = '';
                            showToast('Removed from wishlist', 'info');
                        }
                        if (data.count !== undefined) {
                            const badge = document.querySelector('.wishlist-count');
                            if (badge) {
                                badge.textContent = data.count;
                                badge.style.display = data.count > 0 ? 'inline' : 'none';
                            }
                        }
                    }
                })
                .catch(() => showToast('Error updating wishlist', 'error'));
        });
    });

    // === Add to Cart (AJAX) ===
    document.querySelectorAll('.add-to-cart-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.dataset.url || this.href;
            const form = this.closest('form');

            fetch(url, {
                method: 'POST',
                body: form ? new FormData(form) : null,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Added to cart!', 'success');
                        const badge = document.querySelector('.cart-count');
                        if (badge && data.count !== undefined) {
                            badge.textContent = data.count;
                            badge.style.display = data.count > 0 ? 'inline' : 'none';
                        }
                        // Button animation
                        this.innerHTML = '<i class="fas fa-check me-1"></i>Added!';
                        this.classList.add('btn-success');
                        setTimeout(() => {
                            this.innerHTML = '<i class="fas fa-shopping-cart me-1"></i>Add to Cart';
                            this.classList.remove('btn-success');
                        }, 1500);
                    }
                })
                .catch(() => showToast('Error adding to cart', 'error'));
        });
    });

    // === Remove from Cart ===
    document.querySelectorAll('.remove-cart-item').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            if (confirm('Remove this item from cart?')) {
                this.closest('form').submit();
            }
        });
    });

    // === Search Suggestions ===
    const searchInput = document.querySelector('#searchInput');
    const searchResults = document.querySelector('#searchResults');
    let searchTimeout;

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            searchTimeout = setTimeout(() => {
                fetch(`/api/products/search?q=${encodeURIComponent(query)}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.products && data.products.length > 0) {
                            let html = '';
                            data.products.forEach(p => {
                                html += `<a href="/products/${p.slug}" class="dropdown-item py-2">
                                    <strong>${p.name}</strong>
                                    <small class="text-muted ms-2">$${p.price.toFixed(2)}</small>
                                </a>`;
                            });
                            searchResults.innerHTML = html;
                            searchResults.style.display = 'block';
                        } else {
                            searchResults.innerHTML = '<div class="dropdown-item text-muted">No results found</div>';
                            searchResults.style.display = 'block';
                        }
                    })
                    .catch(() => { searchResults.style.display = 'none'; });
            }, 300);
        });

        // Close search on click outside
        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    // === Payment Method Selection ===
    document.querySelectorAll('.payment-method').forEach(function (method) {
        method.addEventListener('click', function () {
            document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
            this.querySelector('input[type="radio"]').checked = true;

            // Show/hide payment instructions
            const instructions = document.querySelector('.payment-instructions');
            const methodType = this.dataset.method;
            if (instructions) {
                if (methodType === 'online') {
                    instructions.style.display = 'block';
                } else {
                    instructions.style.display = 'none';
                }
            }
        });
    });

    // === Rating Stars ===
    document.querySelectorAll('.rating-input .fa-star').forEach(function (star) {
        star.addEventListener('click', function () {
            const rating = this.dataset.rating;
            const container = this.closest('.rating-input');
            container.querySelectorAll('.fa-star').forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
            const input = container.querySelector('input[type="hidden"]');
            if (input) input.value = rating;
        });

        star.addEventListener('mouseenter', function () {
            const rating = this.dataset.rating;
            const container = this.closest('.rating-input');
            container.querySelectorAll('.fa-star').forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });

    document.querySelectorAll('.rating-input').forEach(function (container) {
        container.addEventListener('mouseleave', function () {
            const input = this.querySelector('input[type="hidden"]');
            const currentRating = input ? parseInt(input.value) : 0;
            this.querySelectorAll('.fa-star').forEach((s, i) => {
                if (i < currentRating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });

    // === Delete Confirmation ===
    document.querySelectorAll('.confirm-delete').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // === Tooltips ===
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        new bootstrap.Tooltip(el);
    });

    // === Image Preview on Upload ===
    document.querySelectorAll('.image-upload-preview').forEach(function (input) {
        input.addEventListener('change', function () {
            const preview = document.querySelector(this.dataset.preview);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // === Lazy Loading Images ===
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function (img) {
            imageObserver.observe(img);
        });
    }

});

// === Helper Functions ===

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function showToast(message, type) {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    const toast = document.createElement('div');
    toast.className = `flash-message ${type || 'info'}`;
    toast.innerHTML = `
        <span><i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>${message}</span>
        <button type="button" class="btn-close" aria-label="Close"></button>
    `;
    container.appendChild(toast);

    setTimeout(function () {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(function () { toast.remove(); }, 300);
    }, 3000);

    toast.querySelector('.btn-close').addEventListener('click', function () {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(function () { toast.remove(); }, 300);
    });
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}
