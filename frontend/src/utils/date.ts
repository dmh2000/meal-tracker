const PACIFIC_TIMEZONE = 'America/Los_Angeles';

/**
 * Get today's date in Pacific Time as YYYY-MM-DD string.
 */
export function getPacificToday(): string {
  const now = new Date();
  const pacificDate = now.toLocaleDateString('en-CA', {
    timeZone: PACIFIC_TIMEZONE,
  });
  return pacificDate;
}
