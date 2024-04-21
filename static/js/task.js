function toggleFormVisibility() {
    var manager = document.getElementById("manager_use").getAttribute("manager");
    var user = document.getElementById("manager_use").getAttribute("username");
    var container_manager = document.getElementById("manager_use");
    if (user === manager) {
        container_manager.style.display = "block";
    } else {
        container_manager.style.display = "none";
    }
}

window.onload = toggleFormVisibility;

document.getElementById('edit-task-btn').addEventListener('click', function () {
    var xhr = new XMLHttpRequest();
    var editUrl = this.getAttribute('data-edit-url');
    xhr.open('GET', editUrl, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onload = function () {
        if (xhr.status === 200) {
            document.getElementById('edit-task-form-container').innerHTML = xhr.responseText;
        } else {
            console.error('Failed to load edit task form');
        }
    };
    xhr.send();
});