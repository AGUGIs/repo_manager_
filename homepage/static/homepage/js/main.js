// Обновляем год в общем подвале; без JavaScript остаётся серверный год.
const yearElement = document.getElementById('current-year');
if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}
