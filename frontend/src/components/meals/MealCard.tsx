import { Link } from 'react-router-dom';
import type { MealType, MealLogEntry } from '../../types';
import { MEAL_TYPE_LABELS } from '../../types';

interface MealCardProps {
  mealType: MealType;
  entry: MealLogEntry;
}

const mealIcons: Record<MealType, string> = {
  breakfast: '🌅',
  morning_snack: '🍎',
  lunch: '🍱',
  afternoon_snack: '🥤',
  dinner: '🍽️',
  evening_snack: '🌙',
};

export function MealCard({ mealType, entry }: MealCardProps) {
  const hasItems = entry.items.length > 0;

  return (
    <Link
      to={`/meal/${mealType}`}
      className="card-hover block p-4 active:scale-[0.98]"
    >
      <div className="flex items-center gap-3">
        <div className="text-2xl">{mealIcons[mealType]}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900">
              {MEAL_TYPE_LABELS[mealType]}
            </h3>
            {hasItems && (
              <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
            )}
          </div>
          {entry.meal_name && (
            <p className="text-sm text-gray-500 truncate">{entry.meal_name}</p>
          )}
        </div>
        <div className="text-right">
          <p className={`font-semibold ${hasItems ? 'text-primary-600' : 'text-gray-400'}`}>
            {entry.calories}
          </p>
          <p className="text-xs text-gray-400">cal</p>
        </div>
      </div>
    </Link>
  );
}
