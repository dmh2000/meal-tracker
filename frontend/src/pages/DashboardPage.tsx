import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { MealCard } from '../components/meals/MealCard';
import { Spinner } from '../components/ui/Spinner';
import { log } from '../services/api';
import type { DailyLog, MealType } from '../types';
import { MEAL_TYPES } from '../types';
import { getPacificToday } from '../utils/date';

export function DashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const today = getPacificToday();

  // Get date from URL or default to today
  const [selectedDate, setSelectedDate] = useState(() => {
    return searchParams.get('date') || today;
  });

  const [dailyLog, setDailyLog] = useState<DailyLog | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Sync URL with selected date
  useEffect(() => {
    if (selectedDate === today) {
      searchParams.delete('date');
    } else {
      searchParams.set('date', selectedDate);
    }
    setSearchParams(searchParams, { replace: true });
  }, [selectedDate, today, searchParams, setSearchParams]);

  // Load available dates
  useEffect(() => {
    log.getDates()
      .then((data) => setAvailableDates(data.dates))
      .catch(() => setAvailableDates([]));
  }, []);

  // Load daily log for selected date
  useEffect(() => {
    setLoading(true);
    setDailyLog(null);  // Reset before fetching new date
    setError('');
    log.getDaily(selectedDate)
      .then(setDailyLog)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [selectedDate]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });
  };

  const goToPreviousDay = () => {
    const current = new Date(selectedDate + 'T12:00:00');  // Use noon to avoid timezone issues
    current.setDate(current.getDate() - 1);
    const year = current.getFullYear();
    const month = String(current.getMonth() + 1).padStart(2, '0');
    const day = String(current.getDate()).padStart(2, '0');
    setSelectedDate(`${year}-${month}-${day}`);
  };

  const goToNextDay = () => {
    const current = new Date(selectedDate + 'T12:00:00');  // Use noon to avoid timezone issues
    current.setDate(current.getDate() + 1);
    const year = current.getFullYear();
    const month = String(current.getMonth() + 1).padStart(2, '0');
    const day = String(current.getDate()).padStart(2, '0');
    setSelectedDate(`${year}-${month}-${day}`);
  };

  const goToToday = () => {
    setSelectedDate(today);
  };

  // Determine if navigation buttons should be disabled
  const isToday = selectedDate === today;
  const oldestDate = availableDates.length > 0 ? availableDates[0] : null;
  const canGoBack = !oldestDate || selectedDate > oldestDate;
  const canGoForward = selectedDate < today;
  const isViewingPast = selectedDate < today;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Date Navigation */}
        <div className={`rounded-lg p-4 ${isViewingPast ? 'bg-amber-50' : 'bg-white'}`}>
          <div className="flex items-center justify-between gap-2">
            {/* Previous Day Button */}
            <button
              onClick={goToPreviousDay}
              disabled={!canGoBack}
              className={`p-2 rounded-lg transition-colors ${
                canGoBack
                  ? 'text-gray-600 hover:bg-gray-100 active:bg-gray-200'
                  : 'text-gray-300 cursor-not-allowed'
              }`}
              aria-label="Previous day"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Date Display */}
            <div className="text-center flex-1">
              <p className={`text-sm uppercase tracking-wide ${isViewingPast ? 'text-amber-600' : 'text-gray-500'}`}>
                {isToday ? 'Today' : 'Past Day'}
              </p>
              <h2 className="text-lg font-medium text-gray-900">{formatDate(selectedDate)}</h2>
            </div>

            {/* Next Day Button */}
            <button
              onClick={goToNextDay}
              disabled={!canGoForward}
              className={`p-2 rounded-lg transition-colors ${
                canGoForward
                  ? 'text-gray-600 hover:bg-gray-100 active:bg-gray-200'
                  : 'text-gray-300 cursor-not-allowed'
              }`}
              aria-label="Next day"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {/* Today Button - Only show when viewing past */}
          {isViewingPast && (
            <button
              onClick={goToToday}
              className="mt-3 w-full py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 rounded-lg transition-colors"
            >
              Jump to Today
            </button>
          )}
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
                date={selectedDate}
              />
            ))}
          </div>
        ) : null}
      </div>
    </Layout>
  );
}
