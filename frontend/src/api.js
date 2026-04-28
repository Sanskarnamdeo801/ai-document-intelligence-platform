const API = import.meta.env.VITE_API_URL;

export const getMetrics = () => fetch(`${API}/api/v1/dashboard/metrics`);
export const getDocs = () => fetch(`${API}/api/v1/documents`);