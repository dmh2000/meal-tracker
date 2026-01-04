import type { User, Food, MealTemplate, DailyLog, LogEntry } from '../types';

const API_BASE = '/api';

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || 'Request failed');
  }

  return response.json();
}

// Auth
export const auth = {
  register: (username: string, password: string) =>
    request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  login: (username: string, password: string, remember_me: boolean = false) =>
    request<User>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password, remember_me }),
    }),

  logout: () =>
    request<{ success: boolean }>('/auth/logout', { method: 'POST' }),

  me: () => request<User>('/auth/me'),
};

// Foods
export const foods = {
  getAll: () => request<Food[]>('/foods'),

  search: (q: string) => request<Food[]>(`/foods/search?q=${encodeURIComponent(q)}`),

  create: (name: string, calories: number) =>
    request<Food>('/foods', {
      method: 'POST',
      body: JSON.stringify({ name, calories }),
    }),
};

// Meals (templates)
export const meals = {
  getAll: () => request<MealTemplate[]>('/meals'),

  get: (id: number) => request<MealTemplate>(`/meals/${id}`),

  create: (name: string, description: string | null, items: { food_id: number; quantity: number }[]) =>
    request<MealTemplate>('/meals', {
      method: 'POST',
      body: JSON.stringify({ name, description, items }),
    }),
};

// User meal log
export const log = {
  getDaily: (date: string) => request<DailyLog>(`/log?date=${date}`),

  get: (id: number) => request<LogEntry>(`/log/${id}`),

  save: (
    meal_type: string,
    meal_date: string,
    meal_name: string | null,
    items: { food_id: number; quantity: number }[]
  ) =>
    request<LogEntry>('/log', {
      method: 'POST',
      body: JSON.stringify({ meal_type, meal_date, meal_name, items }),
    }),

  delete: (id: number) =>
    request<{ success: boolean }>(`/log/${id}`, { method: 'DELETE' }),
};
