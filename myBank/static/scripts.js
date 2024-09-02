window.addEventListener("DOMContentLoaded", (event) => {
    const createAccountBtn = document.getElementById('createAccountBtn');
    if (createAccountBtn) {
        createAccountBtn.addEventListener('click', function() {
            window.location.href = 'create_account';
        });
    }

    const homeLoginBtn = document.getElementById('homeLoginBtn');
    if (homeLoginBtn) {
        homeLoginBtn.addEventListener('click', function() {
            window.location.href = 'login';
        });
    }

    const createPixBtn = document.getElementById('createPixBtn');
    if (createPixBtn) {
        createPixBtn.addEventListener('click', function() {
            window.location.href = 'registerkey';
        });
    }

    const loginBtn = document.getElementById('loginBtn');
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            window.location.href = 'dashboard';
        });
    }
    
    document.getElementById('PixBtn').addEventListener('click', function() {
        window.location.href = '/transfer';
    });
    
});
