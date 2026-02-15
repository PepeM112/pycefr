import { computed, type ComputedRef } from 'vue';
import type { LocationQuery } from 'vue-router';
import { NavigationFailureType, isNavigationFailure, useRoute, useRouter } from 'vue-router';

export interface Query {
  /** The current reactive URL query parameters */
  currentQuery: ComputedRef<LocationQuery>;
  /** Updates the URL query parameters with safety checks */
  updateQuery: (newQuery: LocationQuery) => Promise<void>;
}

/**
 * Composable to manage URL query state.
 * Encapsulates navigation failure handling and prevents out-of-sync updates.
 */
export function useQuery(): Query {
  const route = useRoute();
  const router = useRouter();

  const initialPath = route.path;

  const currentQuery = computed(() => route.query);

  async function updateQuery(newQuery: LocationQuery) {
    if (router.currentRoute.value.path !== initialPath) return;

    const failure = await router.replace({ query: newQuery });

    if (isNavigationFailure(failure)) {
      // Ignore failure caused by navigating to the exact same URL (common in filtering).
      if (failure.type & NavigationFailureType.duplicated) return;

      const fromPath = (failure.from as any).path || failure.from;
      const toPath = (failure.to as any).path || failure.to;

      console.warn(`Failed navigation (${failure.type}): from ${fromPath} to ${toPath}`);
    }
  }

  return { currentQuery, updateQuery };
}
