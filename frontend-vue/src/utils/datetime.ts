import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import localizedFormat from 'dayjs/plugin/localizedFormat';

dayjs.extend(localizedFormat);
dayjs.extend(relativeTime);

/**
 * Formats a date using the browser's local timezone.
 * @param value - Date in Date, String (ISO), or Timestamp format
 * @param format - Format pattern (e.g., 'DD-MM-YYYY')
 */
export function formatDate(
  value: Date | string | number | null | undefined,
  format: string = 'DD-MM-YYYY',
  relative: boolean = false
): string {
  if (!value) return 'N/A';

  const date = dayjs(value);

  if (!date.isValid()) {
    return 'Invalid date';
  }

  if (relative) {
    return date.fromNow();
  }

  return date.format(format);
}
