export type MealType =
  | 'breakfast'
  | 'morning_snack'
  | 'lunch'
  | 'afternoon_snack'
  | 'dinner'
  | 'evening_snack';

export interface User {
  id: number;
  username: string;
}

export interface Food {
  id: number;
  name: string;
  calories: number;
}

export interface MealItem {
  id?: number;
  food_id: number;
  food_name: string;
  calories: number;
  quantity: number;
}

export interface MealTemplate {
  id: number;
  name: string;
  description: string | null;
  items: MealItem[];
  total_calories: number;
}

export interface MealLogEntry {
  log_id: number | null;
  meal_name: string | null;
  items: MealItem[];
  calories: number;
}

export interface DailyLog {
  date: string;
  total_calories: number;
  meals: Record<MealType, MealLogEntry>;
}

export interface LogEntry {
  id: number;
  meal_date: string;
  meal_type: MealType;
  meal_id: number | null;
  meal_name: string | null;
  items: MealItem[];
  total_calories: number;
}

export const MEAL_TYPES: MealType[] = [
  'breakfast',
  'morning_snack',
  'lunch',
  'afternoon_snack',
  'dinner',
  'evening_snack',
];

export const MEAL_TYPE_LABELS: Record<MealType, string> = {
  breakfast: 'Breakfast',
  morning_snack: 'Morning Snack',
  lunch: 'Lunch',
  afternoon_snack: 'Afternoon Snack',
  dinner: 'Dinner',
  evening_snack: 'Evening Snack',
};
