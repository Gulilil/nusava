import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

// Helper function to get token safely (only on client side)
const getAuthToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("jwtToken");
  }
  return null;
};

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const loginBot = async (username: string, password: string) => {
  return axios.post(`${API}/login/`, { username, password });
};

export interface BotConfig {
  likesPerDay: number;
  followsPerDay: number;
  commentsPerDay: number;
  targetAccounts: string[];
  activeHours: string;
}

export interface BotStatus {
  isActive: boolean;
  lastActive: string;
  currentTask: string | null;
}

export const getBotPosts = async () => {
  const res = await axios.get(`${API}/posts/`, {
    headers: getAuthHeaders(),
  });
  return res.data;
};

export const likePost = async (media_url: string) => {
  console.log(API);
  return axios.post(
    `${API}/like/`,
    { media_url },
    { headers: getAuthHeaders() }
  );
};

export const followUser = async (target_username: string) => {
  return axios.post(
    `${API}/follow/`,
    { target_username },
    { headers: getAuthHeaders() }
  );
};

export const commentPost = async (media_url: string, comment: string) => {
  return axios.post(
    `${API}/comment/`,
    { media_url, comment },
    { headers: getAuthHeaders() }
  );
};

export const postPhoto = async (image_path: string, caption: string) => {
  return axios.post(
    `${API}/post/`,
    { image_path, caption },
    { headers: getAuthHeaders() }
  );
};
