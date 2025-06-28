import { AllTourismStatistics, TourismObjectsResponse, TourismStatistics } from "@/types/types";
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

export async function getTourismObjects(): Promise<TourismObjectsResponse> {
  const response = await fetch(`${API}/tourism/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch tourism objects');
  }

  const result = await response.json();
  return result.data;
}

export async function getTourismObjectDetail(objectId: number) {
  const response = await fetch(`${API}/tourism/${objectId}/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch tourism object details');
  }

  const result = await response.json();
  return result.data;
}

export async function getTourismObjectsList() {
  const response = await fetch(`${API}/tourism-objects/list/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch tourism objects list');
  }

  const result = await response.json();
  return result.data;
}

export async function getTourismObjectStatistics(objectId: number, hours: number = 24): Promise<TourismStatistics> {
  const response = await fetch(`${API}/tourism/stats/${objectId}/?hours=${hours}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch tourism object statistics');
  }

  const result = await response.json();
  if (result.status !== 'success') {
    throw new Error(result.message || 'Failed to fetch statistics');
  }
  
  return result.data;
}

export async function getAllTourismStatistics(hours: number = 24): Promise<AllTourismStatistics> {
  const response = await fetch(`${API}/tourism/stats/?hours=${hours}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch all tourism statistics');
  }

  const result = await response.json();
  if (result.status !== 'success') {
    throw new Error(result.message || 'Failed to fetch statistics');
  }
  
  return result.data;
}

export async function schedulePost(data: {
  image_url: string;
  caption: string;
  tourism_object_id?: number;
  scheduled_time: string;
}) {
  const response = await fetch(`${API}/schedule-post/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to schedule post');
  }

  const result = await response.json();
  return result;
}