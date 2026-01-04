import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { Spinner } from '../components/ui/Spinner';
import { log, foods, meals } from '../services/api';
import type { MealType, Food, MealItem, MealTemplate } from '../types';
import { MEAL_TYPE_LABELS, MEAL_TYPES } from '../types';

interface LocalItem {
  food_id: number;
  food_name: string;
  calories: number;
  quantity: number;
}

export function MealPage() {
  const { type } = useParams<{ type: string }>();
  const navigate = useNavigate();
  const mealType = type as MealType;

  const [items, setItems] = useState<LocalItem[]>([]);
  const [mealName, setMealName] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Food search
  const [allFoods, setAllFoods] = useState<Food[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewFood, setShowNewFood] = useState(false);
  const [newFoodName, setNewFoodName] = useState('');
  const [newFoodCalories, setNewFoodCalories] = useState('');

  // Templates
  const [templates, setTemplates] = useState<MealTemplate[]>([]);
  const [showTemplates, setShowTemplates] = useState(false);

  const today = new Date().toISOString().split('T')[0]!;

  // Validate meal type
  useEffect(() => {
    if (!MEAL_TYPES.includes(mealType)) {
      navigate('/');
    }
  }, [mealType, navigate]);

  // Load existing data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [dailyLog, foodList, templateList] = await Promise.all([
          log.getDaily(today),
          foods.getAll(),
          meals.getAll(),
        ]);

        setAllFoods(foodList);
        setTemplates(templateList);

        const entry = dailyLog.meals[mealType];
        if (entry && entry.items.length > 0) {
          setItems(entry.items.map((i: MealItem) => ({
            food_id: i.food_id,
            food_name: i.food_name,
            calories: i.calories,
            quantity: i.quantity,
          })));
          if (entry.meal_name) {
            setMealName(entry.meal_name);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [mealType, today]);

  const totalCalories = items.reduce((sum, item) => sum + item.calories * item.quantity, 0);

  const filteredFoods = searchQuery
    ? allFoods.filter((f) => f.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : allFoods;

  const addFood = useCallback((food: Food) => {
    setItems((prev) => [...prev, {
      food_id: food.id,
      food_name: food.name,
      calories: food.calories,
      quantity: 1,
    }]);
    setSearchQuery('');
  }, []);

  const removeItem = useCallback((index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const updateQuantity = useCallback((index: number, quantity: number) => {
    setItems((prev) => prev.map((item, i) =>
      i === index ? { ...item, quantity: Math.max(0.1, quantity) } : item
    ));
  }, []);

  const handleCreateFood = async (e: React.FormEvent) => {
    e.preventDefault();
    const calories = parseInt(newFoodCalories, 10);
    if (!newFoodName.trim() || isNaN(calories) || calories < 0) return;

    try {
      const food = await foods.create(newFoodName.trim(), calories);
      setAllFoods((prev) => [...prev, food]);
      addFood(food);
      setNewFoodName('');
      setNewFoodCalories('');
      setShowNewFood(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create food');
    }
  };

  const handleLoadTemplate = (template: MealTemplate) => {
    setItems(template.items.map((i) => ({
      food_id: i.food_id,
      food_name: i.food_name,
      calories: i.calories,
      quantity: i.quantity,
    })));
    setMealName(template.name);
    setShowTemplates(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');

    try {
      await log.save(
        mealType,
        today,
        mealName.trim() || null,
        items.map((i) => ({ food_id: i.food_id, quantity: i.quantity }))
      );
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to="/" className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">
              {MEAL_TYPE_LABELS[mealType]}
            </h2>
            <p className="text-sm text-gray-500">{totalCalories} calories</p>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Meal Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Meal Name (optional)
          </label>
          <input
            type="text"
            value={mealName}
            onChange={(e) => setMealName(e.target.value)}
            placeholder="Name this meal to save as template"
            className="input"
          />
        </div>

        {/* Load from Template */}
        {templates.length > 0 && (
          <div>
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="btn-secondary text-sm"
            >
              Load from Template
            </button>

            {showTemplates && (
              <div className="mt-2 card divide-y divide-gray-100 max-h-48 overflow-y-auto">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => handleLoadTemplate(template)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                  >
                    <p className="font-medium text-gray-900">{template.name}</p>
                    <p className="text-sm text-gray-500">{template.total_calories} cal</p>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Food Items */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Food Items</h3>

          {items.length === 0 ? (
            <p className="text-gray-400 text-sm py-4 text-center">No items added yet</p>
          ) : (
            <div className="space-y-2">
              {items.map((item, index) => (
                <div key={index} className="card p-3 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{item.food_name}</p>
                    <p className="text-sm text-gray-500">
                      {Math.round(item.calories * item.quantity)} cal
                    </p>
                  </div>
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateQuantity(index, parseFloat(e.target.value) || 1)}
                    min="0.1"
                    step="0.1"
                    className="w-16 px-2 py-1 text-center border border-gray-300 rounded-lg text-sm"
                  />
                  <button
                    onClick={() => removeItem(index)}
                    className="text-red-500 hover:text-red-600 p-1"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Food */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Add Food</h3>

          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search foods..."
            className="input mb-2"
          />

          {searchQuery && (
            <div className="card divide-y divide-gray-100 max-h-48 overflow-y-auto">
              {filteredFoods.length === 0 ? (
                <p className="px-4 py-3 text-gray-500 text-sm">No foods found</p>
              ) : (
                filteredFoods.slice(0, 10).map((food) => (
                  <button
                    key={food.id}
                    onClick={() => addFood(food)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex justify-between items-center"
                  >
                    <span className="font-medium text-gray-900">{food.name}</span>
                    <span className="text-sm text-gray-500">{food.calories} cal</span>
                  </button>
                ))
              )}
            </div>
          )}

          <button
            onClick={() => setShowNewFood(!showNewFood)}
            className="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            + Create New Food
          </button>

          {showNewFood && (
            <form onSubmit={handleCreateFood} className="mt-2 card p-4 space-y-3">
              <input
                type="text"
                value={newFoodName}
                onChange={(e) => setNewFoodName(e.target.value)}
                placeholder="Food name"
                className="input"
                required
              />
              <input
                type="number"
                value={newFoodCalories}
                onChange={(e) => setNewFoodCalories(e.target.value)}
                placeholder="Calories"
                className="input"
                min="0"
                required
              />
              <div className="flex gap-2">
                <button type="submit" className="btn-primary text-sm">
                  Add Food
                </button>
                <button
                  type="button"
                  onClick={() => setShowNewFood(false)}
                  className="btn-secondary text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary w-full"
        >
          {saving ? 'Saving...' : 'Save Meal'}
        </button>
      </div>
    </Layout>
  );
}
