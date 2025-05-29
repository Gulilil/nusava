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

// Mock API functions
export async function getBotStatus(): Promise<BotStatus> {
  return {
    isActive: true,
    lastActive: new Date().toISOString(),
    currentTask: "Liking posts from @travel_lover",
  }
}

export async function getBotConfig(): Promise<BotConfig> {
  return {
    likesPerDay: 50,
    followsPerDay: 20,
    commentsPerDay: 10,
    targetAccounts: ["@fashion", "@travel", "@food"],
    activeHours: "9:00 AM - 6:00 PM",
  }
}

export async function updateBotConfig(config: Partial<BotConfig>): Promise<BotConfig> {
  // In a real app, this would update the config in a database
  console.log("Updating bot config:", config)
  return {
    ...(await getBotConfig()),
    ...config,
  }
}

export async function startBot(): Promise<BotStatus> {
  // In a real app, this would start the bot
  console.log("Starting bot")
  return {
    isActive: true,
    lastActive: new Date().toISOString(),
    currentTask: "Starting up...",
  }
}

export async function stopBot(): Promise<BotStatus> {
  // In a real app, this would stop the bot
  console.log("Stopping bot")
  return {
    isActive: false,
    lastActive: new Date().toISOString(),
    currentTask: null,
  }
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
