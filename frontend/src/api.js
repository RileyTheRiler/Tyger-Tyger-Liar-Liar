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
    // Sentinel: Removed insecure remote shutdown capability.
    // This is now a client-side only operation (closing the window/clearing state)
    // or requires manual server termination.
    console.log("Remote shutdown disabled for security.");
    return true;
};
