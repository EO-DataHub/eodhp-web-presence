const clearForm = () => {
    document.getElementById('accessKey').value = '';
    document.getElementById('secretKey').value = '';
    document.getElementById('sessionToken').value = '';
    document.getElementById('CredentialsManagement').classList.add('d-none');
}

const populateForm = (data) => {
    document.getElementById('accessKey').value = data.AccessKeyId;
    document.getElementById('secretKey').value = data.SecretAccessKey;
    document.getElementById('sessionToken').value = data.SessionToken;
    document.getElementById('CredentialsManagement').classList.remove('d-none');
}

const displayLoading = () => {
    document.getElementById('loadingSpinner').classList.remove('d-none');
    document.getElementById('usernameForm').classList.add('d-none');
    document.getElementById('CredentialsManagement').classList.add('d-none');
}

const hideLoading = () => {
    document.getElementById('loadingSpinner').classList.add('d-none');
    document.getElementById('usernameForm').classList.remove('d-none');
}

const copyToClipboard = (text) => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

const getCredentials = async () => {
    const username = document.getElementById('username').value;
    displayLoading();

    try {
        const response = await fetch(`/home/get_credentials?username=${username}`);
        const data = await response.json();
        if (data.error) {
            clearForm();
            hideLoading();
            alert(data.error);
        } else {
            clearForm();
            hideLoading();
            populateForm(data);
        }
    } catch (error) {
        clearForm();
        hideLoading();
    }
}

const refreshCredentials = async () => {
    const username = document.getElementById('username').value;
    displayLoading();
    try {
        const response = await fetch(`/home/refresh_credentials?username=${username}`);
        const data = await response.json();
        clearForm();
        populateForm(data);
        hideLoading();
    } catch (error) {
        clearForm();
        hideLoading();

    }
}

const revokeCredentials = () => {
    clearForm();
}

window.getCredentials = getCredentials;
window.refreshCredentials = refreshCredentials;
window.revokeCredentials = revokeCredentials;
