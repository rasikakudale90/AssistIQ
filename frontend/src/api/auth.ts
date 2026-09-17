import { apiClient } from './client';
import { AuthTokens, User } from './types';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export async function loginApi(email: string, password: string): Promise<{ tokens: AuthTokens; user: User }> {
  const res = await apiClient.post<TokenResponse>('/auth/login', {
    email,
    password,
  });

  const { access_token, refresh_token, user } = res.data;
  localStorage.setItem('assistiq_token', access_token);
  localStorage.setItem('assistiq_refresh_token', refresh_token);
  localStorage.setItem('assistiq_user', JSON.stringify(user));

  return {
    tokens: { access_token, refresh_token, token_type: res.data.token_type },
    user,
  };
}

export async function getMeApi(): Promise<User> {
  const res = await apiClient.get<User>('/auth/me');
  return res.data;
}

export async function signupApi(
  email: string,
  password: string,
  role: string = 'Requester',
  site: string = 'Main Facility'
): Promise<User> {
  const res = await apiClient.post<User>('/auth/signup', {
    email,
    password,
    role,
    site,
  });
  return res.data;
}
