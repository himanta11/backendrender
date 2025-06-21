// Authentication Utilities
class AuthManager {
    constructor() {
        this.token = localStorage.getItem('token');
        this.refreshInProgress = false;
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.token;
    }

    // Get current token
    getToken() {
        return this.token;
    }

    // Set token
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    // Remove token (logout)
    removeToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    // Verify token validity
    async verifyToken() {
        if (!this.token) {
            return false;
        }

        try {
            const response = await fetch(API_CONFIG.baseUrl + API_CONFIG.endpoints.users.me, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                return true;
            } else if (response.status === 401) {
                // Token is invalid, try to refresh
                return await this.refreshToken();
            }
            return false;
        } catch (error) {
            console.error('Token verification failed:', error);
            return false;
        }
    }

    // Refresh token
    async refreshToken() {
        if (this.refreshInProgress) {
            // Wait for ongoing refresh
            return new Promise((resolve) => {
                const checkRefresh = setInterval(() => {
                    if (!this.refreshInProgress) {
                        clearInterval(checkRefresh);
                        resolve(!!this.token);
                    }
                }, 100);
            });
        }

        this.refreshInProgress = true;

        try {
            const response = await fetch(API_CONFIG.baseUrl + API_CONFIG.endpoints.auth.refresh, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.setToken(data.access_token);
                this.refreshInProgress = false;
                return true;
            } else {
                // Refresh failed, user needs to login again
                this.removeToken();
                this.refreshInProgress = false;
                return false;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.removeToken();
            this.refreshInProgress = false;
            return false;
        }
    }

    // Get authenticated headers for API requests
    async getAuthHeaders() {
        if (!this.token) {
            throw new Error('No authentication token');
        }

        // Verify token before making request
        const isValid = await this.verifyToken();
        if (!isValid) {
            throw new Error('Authentication failed');
        }

        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    // Handle authentication errors
    handleAuthError() {
        this.removeToken();
        window.location.href = 'auth.html';
    }

    // Auto-refresh token periodically (every 6 days)
    startAutoRefresh() {
        // Refresh token every 6 days (6 * 24 * 60 * 60 * 1000 = 518400000 ms)
        setInterval(async () => {
            if (this.token) {
                await this.refreshToken();
            }
        }, 518400000);
    }

    // Check authentication on page load
    async checkAuthOnLoad() {
        if (this.token) {
            const isValid = await this.verifyToken();
            if (!isValid) {
                this.handleAuthError();
            }
        }
    }
}

// Create global auth manager instance
const authManager = new AuthManager();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
} 