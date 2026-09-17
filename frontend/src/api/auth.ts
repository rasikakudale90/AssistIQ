import { apiClient } from './client';
import { AuthTokens, User } from './types';

export async function loginApi(email: string, password: string): Promise<{ tokens: AuthTokens; user: User }> {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const res = await apiClient.post<AuthTokens>('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  const tokens = res.data;
  localStorage.setItem('assistiq_token', tokens.access_token);
  localStorage.setItem('assistiq_refresh_token', tokens.refresh_token);

  const userRes = await apiClient.get<User>('/auth/me');
  localStorage.setItem('assistiq_user', JSON.stringify(userRes.data));

  return { tokens, user: userRes.data };
}

export async function getMeApi(): Promise<User> {
  const res = await apiClient.get<User>('/auth/me');
  return res.data;
}

export async function signupApi(email: string, password: string, role?: string): Promise<User> {
  const res = await apiClient.post<User>('/auth/signup', { email, password, role });
  return res.data;
}
