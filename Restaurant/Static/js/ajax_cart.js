/**
 * AJAX Cart & Wishlist Functionality
 * Handles add-to-cart and wishlist toggle without page reloads
 */

(function () {
    'use strict';

    // Get CSRF token from cookie (Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Toast notification system
    function showToast(message, type = 'success') {
        // Remove existing toast if any
        const existingToast = document.querySelector('.ajax-toast');
        if (existingToast) {
            existingToast.remove();
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'ajax-toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            max-width: 300px;
        `;

        if (type === 'success') {
            toast.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
        } else if (type === 'error') {
            toast.style.background = 'linear-gradient(135deg, #dc3545, #c82333)';
        } else {
            toast.style.background = 'linear-gradient(135deg, #ffc107, #e0a800)';
            toast.style.color = '#333';
        }

        toast.textContent = message;
        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Add CSS animation for toast
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .ajax-add-cart:hover, .ajax-wishlist:hover {
            transform: scale(1.1);
            transition: transform 0.2s;
        }
        .ajax-add-cart.adding {
            pointer-events: none;
            opacity: 0.7;
        }
    `;
    document.head.appendChild(style);

    // Update cart count badge
    function updateCartCount(count) {
        let badge = document.querySelector('.cart-count-badge');
        if (!badge) {
            // Create badge if it doesn't exist
            const cartLink = document.querySelector('.cart_link');
            if (cartLink) {
                badge = document.createElement('span');
                badge.className = 'cart-count-badge';
                badge.style.cssText = `
                    position: absolute;
                    top: -8px;
                    right: -8px;
                    background: #ffbe33;
                    color: #222;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                `;
                cartLink.style.position = 'relative';
                cartLink.appendChild(badge);
            }
        }
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
            // Add a little bounce animation
            badge.style.animation = 'none';
            badge.offsetHeight; // Trigger reflow
            badge.style.animation = 'bounce 0.3s ease';
        }
    }

    // Add bounce animation for badge
    const bounceStyle = document.createElement('style');
    bounceStyle.textContent = `
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.3); }
        }
    `;
    document.head.appendChild(bounceStyle);

    // Fetch initial cart count on page load
    function fetchCartCount() {
        fetch('/api/cart/count/')
            .then(response => response.json())
            .then(data => {
                updateCartCount(data.cart_count);
            })
            .catch(err => console.error('Error fetching cart count:', err));
    }

    // Handle Add to Cart click
    function handleAddToCart(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        const itemId = btn.dataset.itemId;

        if (!itemId) return;

        btn.classList.add('adding');

        fetch(`/api/cart/add/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                btn.classList.remove('adding');
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    updateCartCount(data.cart_count);
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(err => {
                btn.classList.remove('adding');
                showToast('Error adding to cart', 'error');
                console.error('Add to cart error:', err);
            });
    }

    // Handle Wishlist toggle click
    function handleWishlistToggle(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        const itemId = btn.dataset.itemId;

        if (!itemId) return;

        fetch(`/api/wishlist/toggle/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                if (response.status === 401) {
                    window.location.href = '/login/';
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return;

                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    // Toggle heart icon style
                    const icon = btn.querySelector('i');
                    if (icon) {
                        if (data.in_wishlist) {
                            btn.classList.add('in-wishlist');
                            icon.style.color = '#fff';
                        } else {
                            btn.classList.remove('in-wishlist');
                        }
                    }
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(err => {
                showToast('Error updating wishlist', 'error');
                console.error('Wishlist toggle error:', err);
            });
    }

    // Initialize event listeners
    function init() {
        // Fetch cart count on load
        fetchCartCount();

        // Add to Cart buttons
        document.querySelectorAll('.ajax-add-cart').forEach(btn => {
            btn.addEventListener('click', handleAddToCart);
        });

        // Wishlist buttons
        document.querySelectorAll('.ajax-wishlist').forEach(btn => {
            btn.addEventListener('click', handleWishlistToggle);
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
