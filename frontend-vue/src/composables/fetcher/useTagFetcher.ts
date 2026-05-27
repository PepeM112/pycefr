import { getTags } from '@/client';
import { createFetcher } from './createFetcher';
import type { FetcherOptions, ItemFetcher } from '@/types/fetcher';

export function useTagFetcher(options: FetcherOptions = {}): ItemFetcher {
  return createFetcher(
    getTags,
    items => (items as string[]).map(tag => ({ label: tag, value: tag })),
    'error.fetching.tags',
    options
  );
}
