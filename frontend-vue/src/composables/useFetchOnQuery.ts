import { watch } from 'vue';
import { useRoute } from 'vue-router';
import { useQuery } from './useQuery'; // Import logic inside

interface FetchOptions {
  /** Parameters that should NOT trigger a new request on change. */
  ignoreParams?: string[];
  /** Wait time (ms) to execute the fetcher after the last change. */
  debounceWait?: number;
  /** If true, executes the fetcher immediately on component mount (onMounted).
   * The first execution skips the debounce to be instant. */
  immediate?: boolean;
}

/**
 * Synchronizes a data-fetching function with changes in the URL query parameters.
 *
 * PURPOSE:
 * Acts as a bridge between the browser's URL and API calls.
 * Observes the current route's query and triggers a fetcher whenever relevant
 * parameters change, supporting debouncing to avoid unnecessary requests.
 *
 * ARCHITECTURAL NOTE:
 * Follows a strict unidirectional flow (URL → fetcher).
 * 1. No URL updates: this composable only reacts to the URL, never writes to it.
 *    Writing is the responsibility of the caller (useFilter, usePagination, useSorting).
 *    This prevents infinite loops: UI → URL change → useFetchOnQuery → URL change → ...
 * 2. Single Responsibility: decouples the "when to fetch" concern from the "what to fetch"
 *    logic, which lives in the fetcher function provided by the caller.
 * 3. Route-scoped: automatically stops reacting if the user navigates away from the
 *    route where the composable was initialized, preventing stale fetches.
 * 4. Consistency: by routing all fetches through URL changes, browser history (Back/Forward)
 *    and deep-linking work out of the box — reloading the page or sharing the URL
 *    will always reproduce the same fetch.
 *
 * @param fetcher - The function to execute when relevant query parameters change.
 * @param options - Configuration for debouncing, immediate execution, and ignored parameters.
 */
export function useFetchOnQuery(fetcher: () => Promise<void> | void, options: FetchOptions = {}) {
  const route = useRoute();
  const { currentQuery } = useQuery();

  const initialPath = route.path;
  let timeout: ReturnType<typeof setTimeout> | null = null;

  /**
   * Executes the fetcher function.
   * @param force - If true, ignores the debounceWait (used for initial mount).
   */
  const executeFetch = (force: boolean = false) => {
    if (timeout) clearTimeout(timeout);

    if (force || !options.debounceWait) {
      fetcher();
      return;
    }

    timeout = setTimeout(() => {
      fetcher();
    }, options.debounceWait);
  };

  watch(
    currentQuery,
    (newQ, oldQ) => {
      if (route.path !== initialPath) return;

      if (!oldQ) {
        executeFetch(true);
        return;
      }

      // Logic to detect changes in non-ignored parameters
      const changedKeys = Object.keys({ ...newQ, ...oldQ }).filter(key => newQ[key] !== oldQ[key]);
      const hasRelevantChanges = changedKeys.some(key => !options.ignoreParams?.includes(key));

      if (hasRelevantChanges) executeFetch();
    },
    { deep: true, immediate: options.immediate }
  );
}
