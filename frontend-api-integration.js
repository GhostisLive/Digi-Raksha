// API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Auth utilities
class AuthService {
    static getToken() {
        return localStorage.getItem('access_token');
    }
    
    static setToken(token) {
        localStorage.setItem('access_token', token);
    }
    
    static removeToken() {
        localStorage.removeItem('access_token');
    }
    
    static getAuthHeaders() {
        const token = this.getToken();
        return token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        } : {
            'Content-Type': 'application/json'
        };
    }
    
    static isLoggedIn() {
        return !!this.getToken();
    }
}

// API service
class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: AuthService.getAuthHeaders(),
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                if (response.status === 401) {
                    AuthService.removeToken();
                    // Redirect to login if needed
                    throw new Error('Authentication failed');
                }
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    // Authentication
    static async login(govIdNumber, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                gov_id_number: govIdNumber,
                password: password
            })
        });
        
        if (data.access_token) {
            AuthService.setToken(data.access_token);
        }
        
        return data;
    }
    
    static async register(userData) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (data.access_token) {
            AuthService.setToken(data.access_token);
        }
        
        return data;
    }
    
    static async getCurrentUser() {
        return await this.request('/auth/me');
    }
    
    // SOS Alerts
    static async createSOSAlert(sosData) {
        return await this.request('/sos/', {
            method: 'POST',
            body: JSON.stringify(sosData)
        });
    }
    
    static async getSOSAlerts() {
        return await this.request('/sos/');
    }
    
    static async getNearbySOSAlerts(latitude, longitude, radius = 10) {
        return await this.request(`/sos/nearby?latitude=${latitude}&longitude=${longitude}&radius_km=${radius}`);
    }
    
    static async markSafe(latitude, longitude, message = 'User marked as safe') {
        return await this.request('/sos/safe', {
            method: 'POST',
            body: JSON.stringify({
                latitude,
                longitude,
                message
            })
        });
    }
    
    // Incidents
    static async createIncident(incidentData) {
        return await this.request('/incidents/', {
            method: 'POST',
            body: JSON.stringify(incidentData)
        });
    }
    
    static async getIncidents() {
        return await this.request('/incidents/');
    }
    
    // Missing Persons
    static async reportMissingPerson(missingPersonData) {
        return await this.request('/missing/', {
            method: 'POST',
            body: JSON.stringify(missingPersonData)
        });
    }
    
    static async getMissingPersons(search = '') {
        const searchParam = search ? `?search=${encodeURIComponent(search)}` : '';
        return await this.request(`/missing/${searchParam}`);
    }
    
    // Community Posts
    static async createCommunityPost(postData) {
        return await this.request('/community/', {
            method: 'POST',
            body: JSON.stringify(postData)
        });
    }
    
    static async getCommunityPosts(category = '') {
        const categoryParam = category ? `?category=${category}` : '';
        return await this.request(`/community/${categoryParam}`);
    }
}

// Usage example in your existing code:
// Replace the form submission handlers with API calls

// Example: Update login form handler
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const govIdNumber = document.getElementById('login-id-number').value;
    const password = document.getElementById('login-password').value;
    
    try {
        await ApiService.login(govIdNumber, password);
        // Show success message
        alert('Login successful!');
        enterMainApp();
    } catch (error) {
        // Show error message
        alert('Login failed: ' + error.message);
    }
});

// Example: Update registration form handler
document.getElementById('registration-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
        first_name: formData.get('first-name'),
        middle_name: formData.get('middle-name') || null,
        last_name: formData.get('last-name'),
        city: formData.get('city'),
        gov_id_type: formData.get('gov-id-type'),
        gov_id_number: formData.get('gov-id-number'),
        password: 'temporary-password', // You'll need to add a password field
        photo_url: null // Handle photo upload separately
    };
    
    try {
        await ApiService.register(userData);
        alert('Registration successful!');
        enterMainApp();
    } catch (error) {
        alert('Registration failed: ' + error.message);
    }
});

// Example: SOS button handler
document.getElementById('sosButton').addEventListener('click', async () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            
            try {
                await ApiService.createSOSAlert({
                    latitude,
                    longitude,
                    location_description: 'Emergency location',
                    emergency_type: 'General Emergency'
                });
                alert('SOS alert sent successfully!');
            } catch (error) {
                alert('Failed to send SOS alert: ' + error.message);
            }
        });
    } else {
        alert('Geolocation is not supported by this browser.');
    }
});

// Example: Safe button handler
document.getElementById('safeButton').addEventListener('click', async () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            
            try {
                await ApiService.markSafe(latitude, longitude);
                alert('Marked as safe successfully!');
            } catch (error) {
                alert('Failed to mark as safe: ' + error.message);
            }
        });
    } else {
        alert('Geolocation is not supported by this browser.');
    }
});