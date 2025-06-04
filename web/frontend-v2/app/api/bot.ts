import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_BASE_URL; 

export const loginBot = async (username: string, password: string) => {
  return axios.post(`${API}/login/`, { username, password });
};

export interface BotConfig {
  likesPerDay: number
  followsPerDay: number
  commentsPerDay: number
  targetAccounts: string[]
  activeHours: string
}

export interface BotStatus {
  isActive: boolean
  lastActive: string
  currentTask: string | null
}

const token = localStorage.getItem("jwtToken");

export const getBotPosts = async () => {
  const res = await axios.get(`${API}/posts/`, {
    headers: { Authorization: token ? `Bearer ${token}` : "" },
  });
  return res.data;
};

export const likePost = async (media_url: string) => {
  console.log(API)
  return axios.post(
    `${API}/like/`,
    { media_url },
    { headers: { Authorization: token ? `Bearer ${token}` : "" } }
  );
};

export const followUser = async (target_username: string) => {
  return axios.post(
    `${API}/follow/`,
    { target_username },
    { headers: { Authorization: token ? `Bearer ${token}` : "" } }
  );
};

export const commentPost = async (media_url: string, comment: string) => {
  return axios.post(
    `${API}/comment/`,
    { media_url, comment },
    { headers: { Authorization: token ? `Bearer ${token}` : "" } }
  );
};

export const postPhoto = async (image_path: string, caption: string) => {
  return axios.post(
    `${API}/post/`,
    { image_path, caption },
    { headers: { Authorization: token ? `Bearer ${token}` : "" } }
  );
};

export const sharePost = async (media_url: string, target_usernames: string[]) => {
  return axios.post(
    `${API}/share/`,
    { media_url, target_usernames },
    { headers: { Authorization: token ? `Bearer ${token}` : "" } }
  );
};
