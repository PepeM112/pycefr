import { watch, type WatchSource } from 'vue';
import { useRoute, type LocationQuery } from 'vue-router';

interface FetchOptions {
  /** * Parameters that should NOT trigger a new request on change.
   */
  ignoreParams?: string[];
  /** * Wait time (ms) to execute the fetcher after the last change.
   */
  debounceWait?: number;
  /** * If true, executes the fetcher immediately on component mount (onMounted).
   * The first execution skips the debounce to be instant.
   */
  immediate?: boolean;
}

/**
 * Synchronizes a data-fetching function with changes in the URL query parameters.
 * * PURPOSE:
 * This composable acts as a bridge between the browser's URL and your API calls.
 * It observes a query source and triggers a fetcher whenever relevant parameters change,
 * supporting debouncing to optimize performance and "ignore lists" to prevent unnecessary calls.
 *
 * ARCHITECTURAL NOTE:
 * This composable follows a unidirectional flow (URL -> API).
 * 1. Why doesn't it update the URL internally?
 * It prevents infinite loops: UI -> updateQuery -> URL change -> useFetchOnQuery -> updateQuery...
 * 2. Single Responsibility: This hook only reacts to the URL. The responsibility
 * of updating the URL (UI -> URL) lies with the view or a dedicated state manager.
 * 3. Consistency: By forcing all data fetches to go through the URL, we ensure
 * browser history (Back/Forward) and deep-linking work out of the box.
 * * @param querySource - The reactive source of the URL query (usually currentQuery from useQuery).
 * @param path - The specific route path where this fetcher should be active.
 * @param fetcher - The function (usually an API call) to execute when the query changes.
 * @param options - Configuration for debouncing, initial execution, and ignored parameters.
 */
export function useFetchOnQuery(
  querySource: WatchSource<LocationQuery>,
  path: string,
  fetcher: () => Promise<void> | void,
  options: FetchOptions = {}
) {
  const route = useRoute();
  let timeout: ReturnType<typeof setTimeout> | null = null;

  /**
   * Executes the fetcher function.
   * @param force - If true, ignores the debounceWait (used for initial mount).
   */
  const executeFetch = (force: boolean = false) => {
    // Clear any pending execution to reset the debounce timer
    if (timeout) clearTimeout(timeout);

    if (force || !options.debounceWait) {
      fetcher();
      return;
    }

    timeout = setTimeout(() => {
      fetcher();
    }, options.debounceWait);
  };

  // Watch automatically clears its handlers when the component is unmounted
  watch(
    querySource,
    (newQ, oldQ) => {
      // Only trigger the fetcher if the component's route is still active.
      // Prevents "ghost fetches" during navigation transitions.
      if (route.path !== path) return;

      // Handle immediate execution: if oldQ is undefined, it's the first run.
      if (!oldQ) {
        executeFetch(true);
        return;
      }

      if (options.ignoreParams?.length) {
        const hasChanged = Object.keys({ ...newQ, ...oldQ }).some(key => {
          if (options.ignoreParams?.includes(key)) return false;
          return newQ[key] !== oldQ[key];
        });

        if (!hasChanged) return;
      }

      executeFetch();
    },
    { deep: true, immediate: options.immediate }
  );
}
