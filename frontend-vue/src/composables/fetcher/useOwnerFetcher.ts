import { getOwners, type EntityLabelString } from '@/client';
import { createFetcher } from './createFetcher';
import type { FetcherOptions, ItemFetcher } from '@/types/fetcher';

export function useOwnerFetcher(options: FetcherOptions = {}): ItemFetcher {
  return createFetcher(
    getOwners,
    items => (items as EntityLabelString[]).map(owner => ({ label: owner.label, value: owner.id })),
    'error.fetching.owners',
    options
  );
}
