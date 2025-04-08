const baseUrl = window.location.origin;

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-mark-read').forEach(button => {
        button.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            const notificationLink = this.dataset.notificationLink;
            const url = `${baseUrl}/user/notifications/${notificationId}/view/`;

            sendRequest(url, 'POST', function(data) {
                if (data.message === 'Notification marked as viewed') {
                    const notificationItem = button.closest('.notification-item');
                    notificationItem.classList.remove('unread');

                    const badge = notificationItem.querySelector('.notification-badge');
                    if (badge) {
                        badge.remove();
                    }

                    if (notificationLink) {
                        window.location.href = notificationLink;
                    } else {
                        const actionsDiv = button.closest('.notification-actions');
                        if (actionsDiv) {
                            button.remove();
                        }
                    }
                } else {
                    console.error('Failed to mark as read:', data.error);
                }
            });
        });
    });

    document.querySelectorAll('.notification-btn-delete').forEach(button => {
        button.addEventListener('click', function() {

            const notificationId = this.dataset.notificationId;
            const url = `${baseUrl}/user/notifications/${notificationId}/del/`;

            sendRequest(url, 'POST', function(data) {
                console.log(data)
                if (data.message === 'Notification deleted') {
                    const notificationItem = button.closest('.notification-item');
                    notificationItem.style.opacity = '0';
                    notificationItem.style.transition = 'opacity 0.3s ease';

                    setTimeout(() => {
                        notificationItem.remove();

                        if (!document.querySelector('.notification-item')) {
                            const container = document.querySelector('.notifications-user');
                            if (container) {
                                container.innerHTML = '<div class="notification-empty">\n' +
                                    '                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">\n' +
                                    '                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>\n' +
                                    '                        </svg>\n' +
                                    '                        <p>У вас нету новых уведомлений</p>\n' +
                                    '                    </div>';
                            }
                            const notification_svg = document.getElementById('notify-svg');
                            notification_svg.src = '/static/common/svg/notify.svg';
                        }
                    }, 300);
                } else {
                    console.error('Failed to delete notification:', data.error);
                }
            });
        });
    });
});