document.addEventListener("DOMContentLoaded", function () {

    const notificationContainer = document.getElementById("notificationContainer");

    function createNotification(notification) {
        const notificationElement = document.createElement("div");
        notificationElement.classList.add("notification");
        notificationElement.id = `notification_${notification.id}`;
        if (!notification.read) {
            notificationElement.classList.add("unread");
        } else {
            notificationElement.classList.add("read");
        }
        notificationElement.innerHTML = `
        <h3>${notification.type}</h3>
        <p>${notification.content}</p>
        <p class="date">${notification.date}</p>
    `;
        return notificationElement;
    }

    document.addEventListener("DOMContentLoaded", function() {
    fetch('/get_unread_notification_count')
        .then(response => response.json())
        .then(data => {
            const unreadNotificationCountElement = document.getElementById("unreadNotificationCount");
            if (data.unread_notification_count > 0) {
                unreadNotificationCountElement.textContent = data.unread_notification_count;
                unreadNotificationCountElement.style.display = 'inline';
            } else {
                unreadNotificationCountElement.style.display = 'none';
            }
        })
        .catch(error => console.error('Erreur lors de la récupération du nombre de notifications non lues :', error));
});

    function renderNotifications(notifications) {
        notifications.reverse().forEach(notification => {
            const notificationElement = createNotification(notification);
            notificationContainer.appendChild(notificationElement);

        });
    }

    fetch('/get_notifications')
        .then(response => {
            return response.json();
        })
        .then(data => {
            renderNotifications(data.notifications);
        })
});
