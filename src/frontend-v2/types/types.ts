// Authentication & User Types
export interface User {
  id: number;
  username: string;
  email?: string;
}

export interface LoginResponse {
  status: string;
  message: string;
  access: string;
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
  refresh?: string;
}

// Bot Configuration Types
export interface ConfigData {
  temperature: number;
  top_k: number;
  max_token: number;
  max_iteration: number;
}

export interface InstagramStats {
  followers_count: number
  posts_count: number
  all_likes_count: number
  all_comments_count: number
  impressions: number
  reach: number
  engagement_rate: number
}

// Action Log Types
export interface ActionLog {
  id: number;
  username: string;
  action_type: string;
  target: string;
  status: string;
  message: string;
  timestamp: string;
}

// Pagination Types
export interface PaginationInfo {
  current_page: number;
  total_pages: number;
  total_count: number;
  has_next: boolean;
  has_previous: boolean;
}

// API Response Types
export interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
  pagination?: PaginationInfo;
}

// Dashboard Stats Types
export interface DashboardStats {
  total_actions: number;
  recent_actions: number;
  success_rate: number;
  recent_logs: ActionLog[];
  action_types: Record<string, number>;
}

// Instagram Post Types
export type Post = {
  id: string;
  shortcode: string;
  username: string;
  description: string;
};

// Persona Template Types
export interface PersonaTemplate {
  name: string;
  json: string;
}

export interface PersonaData {
  age: number;
  style: string;
  occupation: string;
}

// Form State Types
export interface LoginFormData {
  username: string;
  password: string;
}

// Filter Types
export interface LogFilters {
  action_type: string;
  status: string;
  page: number;
}

export interface PostFilters {
  search: string;
  media_type: string;
  date_range?: {
    start: string;
    end: string;
  };
}

// Component Props Types
export interface NavbarProps {
  title: string;
}

// Error Types
export interface ApiError {
  message: string;
  status?: number;
  field?: string;
}

// Hook Return Types
export interface UseAuthReturn {
  isAuthenticated: boolean;
  isLoading: boolean;
  logout: () => void;
}

// Status Types
export type ActionStatus = "success" | "error" | "failed" | "pending";
export type MediaType = "photo" | "video" | "carousel" | "reel";

export interface AutomationStatus { 
  is_running: boolean;
  user_id?: number;
  thread_name?: string;
  last_run?: string;
  next_run?: string;
  error?: string;
}

export interface TourismObjectMetrics {
  total_posts: number;
  total_likes: number;
  total_comments: number;
  likes_percent_increase: number;
  comments_percent_increase: number;
}

export interface TourismObject {
  id: number;
  name: string;
  object_type: 'hotel' | 'destination';
  location: string;
  rating: number;
  image_url: string;
  metrics: TourismObjectMetrics;
  last_updated: string;
}

export interface TourismObjectsResponse {
  hotels: TourismObject[];
  destinations: TourismObject[];
  total_count: number;
  hotels_count: number;
  destinations_count: number;
}

export interface TourismPost {
  shortcode: string;
  media_id: string;
  caption: string;
  likes: number;
  comments: number;
  likes_change: number;
  comments_change: number;
  posted_at: string;
  last_updated: string;
}

export interface TourismStatistics {
  success: boolean;
  tourism_object: {
    id: number;
    name: string;
    type: string;
    location: string;
  };
  period_hours: number;  
  summary: {
    total_posts: number;
    total_likes: number;
    total_comments: number;
    average_likes: number;
    average_comments: number;
    likes_growth_rate: number;
    comments_growth_rate: number;
  };
  posts: TourismPost[];
}

export interface AllTourismStatistics {
  success: boolean;
  total_objects: number;
  period_hours: number;  
  tourism_objects: TourismStatistics[];
}