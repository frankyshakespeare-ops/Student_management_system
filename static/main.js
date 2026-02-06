// ===== DATE & TIME =====
function updateDateTime() {
    const now = new Date();
    
    // Format: "04 Feb 2026"
    const dateOptions = { day: '2-digit', month: 'short', year: 'numeric' };
    const formattedDate = now.toLocaleDateString('en-GB', dateOptions);
    
    // Mettre à jour l'affichage
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        dateElement.textContent = formattedDate;
    }
    
    // Mettre à jour l'heure en temps réel (optionnel)
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        const timeOptions = { hour: '2-digit', minute: '2-digit', hour12: false };
        const formattedTime = now.toLocaleTimeString('en-GB', timeOptions);
        timeElement.textContent = formattedTime;
    }
}

// ===== DROPDOWNS =====
function initDropdowns() {
    // Notifications dropdown
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationDropdown = document.getElementById('notificationDropdown');
    
    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');
            
            // Fermer l'autre dropdown si ouvert
            const userDropdown = document.getElementById('userDropdown');
            if (userDropdown) userDropdown.classList.remove('show');
        });
    }
    
    // User dropdown
    const userProfileBtn = document.getElementById('userProfileBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userProfileBtn && userDropdown) {
        userProfileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
            this.classList.toggle('active');
            
            // Fermer l'autre dropdown si ouvert
            if (notificationDropdown) notificationDropdown.classList.remove('show');
        });
    }
    
    // Fermer les dropdowns en cliquant ailleurs
    document.addEventListener('click', function() {
        if (notificationDropdown) notificationDropdown.classList.remove('show');
        if (userDropdown) userDropdown.classList.remove('show');
        if (userProfileBtn) userProfileBtn.classList.remove('active');
    });
}

// ===== SIDEBAR TOGGLE (mobile) =====
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            document.querySelector('.main-content').classList.toggle('expanded');
        });
    }
}

// ===== MARK NOTIFICATIONS AS READ =====
function markNotificationAsRead(notificationId) {
    // Envoyer une requête au serveur pour marquer comme lu
    fetch(`/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mettre à jour l'interface
            const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationItem) {
                notificationItem.classList.remove('unread');
                
                // Mettre à jour le compteur
                const badge = document.querySelector('.notification-badge');
                if (badge) {
                    const currentCount = parseInt(badge.textContent);
                    if (currentCount > 1) {
                        badge.textContent = currentCount - 1;
                    } else {
                        badge.remove();
                    }
                }
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les fonctions
    updateDateTime();
    initDropdowns();
    initSidebar();
    
    // Mettre à jour la date chaque minute
    setInterval(updateDateTime, 60000);
    
    // Marquer les notifications comme lues au clic
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            if (notificationId) {
                markNotificationAsRead(notificationId);
            }
        });
    });
});