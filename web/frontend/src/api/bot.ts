import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const loginBot = async (username: string, password: string) => {
  return axios.post(`${API_BASE}/login/`, { username, password });
};

export const getBotPosts = async () => {
  const res = await axios.get(`${API_BASE}/posts/`);
  return res.data;
};
