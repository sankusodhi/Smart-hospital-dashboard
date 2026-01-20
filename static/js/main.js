function toggleUserDropdown() {
    const userSection = document.querySelector('.user-section');
    userSection.classList.toggle('open');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const userSection = document.querySelector('.user-section');
    if (!userSection.contains(event.target)) {
        userSection.classList.remove('open');
    }
});