function toggleNotifications() {
    document.getElementById('notificationDialog').classList.toggle('active');
}

function openNotificationBox() {
    document.getElementById('notificationDialog').classList.remove('active');
    document.getElementById('notificationBox').classList.add('active');
    document.getElementById('notificationCount').style.display = 'none';
    document.getElementById('sidebarNotificationCount').style.display = 'none'; // Hide sidebar count
}

function toggleDetails(id) {
    var detailsRow = document.getElementById(id);
    detailsRow.classList.toggle('hidden');
}
