/**
 * Calculate hours between start and end time
 * Handles overnight shifts automatically
 * @param {string} startTime - Time in HH:MM format
 * @param {string} endTime - Time in HH:MM format
 * @returns {number} Hours worked (rounded to 2 decimals)
 */
export function calculateHours(startTime, endTime) {
  if (!startTime || !endTime) return 0;
  
  const [startHour, startMin] = startTime.split(':').map(Number);
  const [endHour, endMin] = endTime.split(':').map(Number);
  
  // Convert to minutes since midnight
  let startMinutes = startHour * 60 + startMin;
  let endMinutes = endHour * 60 + endMin;
  
  // Handle overnight shift
  if (endMinutes <= startMinutes) {
    endMinutes += 24 * 60; // Add 24 hours
  }
  
  const diffMinutes = endMinutes - startMinutes;
  const hours = diffMinutes / 60;
  
  return Math.round(hours * 100) / 100; // Round to 2 decimals
}

/**
 * Format current date as YYYY-MM-DD
 * @returns {string} Formatted date
 */
export function getCurrentDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Format time as HH:MM from Date object
 * @param {Date} date - Date object
 * @returns {string} Formatted time
 */
export function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}

/**
 * Get current time as HH:MM
 * @returns {string} Current time
 */
export function getCurrentTime() {
  return formatTime(new Date());
}


