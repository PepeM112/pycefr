import { getOwners } from '@/client';
import { createFetcher } from './createFetcher';
import type { FetcherOptions, ItemFetcher } from '@/types/fetcher';

export function useOwnerFetcher(options: FetcherOptions = {}): ItemFetcher {
  return createFetcher(
    getOwners,
    owners => owners.map(owner => ({ label: owner.label, value: owner.id })),
    'error.fetching.owners',
    options
  );
}
