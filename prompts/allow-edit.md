# Feature: Historical Meal Editing with Date Navigation

## Overview
Remove the constraint that only the current day's meals can be edited. Add date navigation to the dashboard so users can view and edit meals from previous days.

## Requirements

### 1. Date Navigation on Dashboard (`DashboardPage.tsx`)

Add a date navigation bar at the top of the dashboard (below the header, above the Total Calories card) with:

- **Left arrow button**: Navigate to the previous day
- **Date display**: Show the currently selected date in a readable format (e.g., "Monday, Jan 6, 2026")
- **Right arrow button**: Navigate to the next day
- **Today button**: Quick link to jump back to today's date

**Navigation constraints:**
- The right arrow should be **disabled** when viewing today's date (cannot go to future)
- The left arrow should be **disabled** when at the oldest day that has any meal data for the user
- Use the API endpoint `GET /api/log/dates` to fetch available dates with data (you may need to create this endpoint)

### 2. State Management Changes

In `DashboardPage.tsx`:
- Replace the hardcoded `const today = getPacificToday()` with `useState` for `selectedDate`
- Initialize `selectedDate` to `getPacificToday()` on mount
- Update the `useEffect` to fetch data for `selectedDate` instead of `today`
- Pass `selectedDate` to `MealCard` components

### 3. MealCard Component Updates (`MealCard.tsx`)

- Accept a new prop `date: string` (the selected date)
- Pass the date as a URL parameter when navigating to the meal editor: `/meal/${mealType}?date=${date}`

### 4. MealPage Updates (`MealPage.tsx`)

- Read the `date` query parameter from the URL (use `useSearchParams`)
- Default to `getPacificToday()` if no date parameter is provided
- Use this date instead of `today` for all API calls (`log.getDaily()` and `log.save()`)
- Update the back navigation to preserve the date context (navigate to `/?date=${date}` or use browser back)

### 5. API Changes (if needed)

If not already available, add an endpoint to `backend/api_server/routes/log_routes.py`:
- `GET /api/log/dates` - Returns a list of dates (YYYY-MM-DD format) where the user has meal data, sorted oldest to newest

### 6. UI/UX Considerations

- Use Tailwind CSS for styling, consistent with the existing design
- Arrow buttons should use chevron icons (e.g., `<` and `>` or SVG chevrons)
- Disabled buttons should have reduced opacity and `cursor-not-allowed`
- The date display should be prominent and clearly indicate which day is being viewed
- Consider adding a subtle visual indicator when viewing a past date (e.g., different background color or badge)

### 7. Behavior for Days Without Data

- Navigation should skip to the next/previous day that has data, OR
- Allow navigation to any day within the range (showing empty meals for days without data)
- Recommended: Allow any day navigation within range so users can add meals to missed days

## Files to Modify

1. `frontend/src/pages/DashboardPage.tsx` - Add date navigation and state
2. `frontend/src/components/meals/MealCard.tsx` - Accept and pass date prop
3. `frontend/src/pages/MealPage.tsx` - Read date from URL params
4. `backend/api_server/routes/log_routes.py` - Add dates endpoint (if needed)
5. `frontend/src/services/api.ts` - Add API call for dates endpoint (if needed)

## Testing Checklist

- [ ] Can navigate backward from today to previous days
- [ ] Can navigate forward from past days back to today
- [ ] Right arrow disabled on today's date
- [ ] Left arrow disabled on oldest available date
- [ ] Today button returns to current date from any past date
- [ ] Editing a past day's meal saves correctly with the correct date
- [ ] Date persists correctly when navigating to/from meal editor
