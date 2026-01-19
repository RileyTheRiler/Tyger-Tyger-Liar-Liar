import axios from 'axios';

const API_URL = 'http://localhost:8001/api';

export const startGame = async () => {
    try {
        const res = await axios.post(`${API_URL}/start`);
        return res.data;
    } catch (err) {
        console.error("API Error", err);
        throw err;
    }
};

export const sendAction = async (input) => {
    try {
        const res = await axios.post(`${API_URL}/action`, { input });
        return res.data;
    } catch (err) {
        console.error("API Error", err);
        throw err;
    }
};

export const shutdownGame = async () => {
    // Client-side mock since server shutdown endpoint was removed for security
    // Endpoint removed for security.
    // Shutdown endpoint removed for security.
    // We just return true to simulate success for the UI.
    // Sentinel: Mocked client-side to prevent network call to removed endpoint
    return Promise.resolve(true);
};
