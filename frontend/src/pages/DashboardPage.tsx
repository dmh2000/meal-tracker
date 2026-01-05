import { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { MealCard } from '../components/meals/MealCard';
import { Spinner } from '../components/ui/Spinner';
import { log } from '../services/api';
import type { DailyLog, MealType } from '../types';
import { MEAL_TYPES } from '../types';
import { getPacificToday } from '../utils/date';

export function DashboardPage() {
  const [dailyLog, setDailyLog] = useState<DailyLog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const today = getPacificToday();

  useEffect(() => {
    setLoading(true);
    log.getDaily(today)
      .then(setDailyLog)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [today]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Date Header */}
        <div className="text-center">
          <p className="text-sm text-gray-500 uppercase tracking-wide">Today</p>
          <h2 className="text-lg font-medium text-gray-900">{formatDate(today)}</h2>
        </div>

        {/* Total Calories Card */}
        <div className="card p-6 text-center bg-gradient-to-br from-primary-500 to-primary-600">
          <p className="text-primary-100 text-sm uppercase tracking-wide">Total Calories</p>
          {loading ? (
            <div className="flex justify-center py-2">
              <Spinner size="sm" />
            </div>
          ) : (
            <p className="text-4xl font-bold text-white mt-1">
              {dailyLog?.total_calories ?? 0}
            </p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Meal Cards */}
        {loading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : dailyLog ? (
          <div className="space-y-3">
            {MEAL_TYPES.map((mealType: MealType) => (
              <MealCard
                key={mealType}
                mealType={mealType}
                entry={dailyLog.meals[mealType]}
              />
            ))}
          </div>
        ) : null}
      </div>
    </Layout>
  );
}
