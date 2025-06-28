// API Configuration
const API_CONFIG = {
    baseUrl: 'https://backendrender-o1bo.onrender.com',
    apiKey: '', // Add your API key here if needed
    endpoints: {
        auth: {
            login: '/auth/login',
            signup: '/auth/register',
            refresh: '/auth/refresh'
        },
        questions: '/questions/',
        chat: '/api/chat',
        explain: '/questions/explain',
        users: {
            me: '/users/me',
            stats: '/users/stats'
        },
        payment: {
            plans: '/payment/plans',
            createOrder: '/payment/create-order',
            verify: '/payment/verify',
            subscription: '/payment/subscription'
        },
        limits: {
            status: '/user/limits',
            check: '/user/check-limit',
            record: '/user/record-usage'
        }
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
} 