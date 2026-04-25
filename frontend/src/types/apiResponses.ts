// Define types matching the backend responses

export interface BaseResponse {
  status: 'success' | 'error';
  error: string | null;
}

export interface RegisterResponse extends BaseResponse {
  message: string;
  user_id: string;
  api_key: string;
}

export interface LoginResponse extends BaseResponse {
  message: string;
  user_id: string;
  api_key: string;
  username: string;
}

export interface UserStatsResponse extends BaseResponse {
  stats: {
    total_conversations: number;
    average_iterations: number;
    total_time_seconds: number;
  };
}