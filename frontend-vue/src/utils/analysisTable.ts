import { type Level, SortDirection, type AnalysisFilePublic } from '@/client';
import type { AnalysisClassPublicWithLevel } from '@/types/analysis';
import type { Sorting } from '@/composables/useSorting';

type ClassWithLabel = AnalysisClassPublicWithLevel & { translatedLabel: string };

export function groupClassesBySelection(
  fileClasses: AnalysisFilePublic[],
  selectedFilePaths: Set<string>,
  getClassLevel: (classId: number) => Level
): AnalysisClassPublicWithLevel[] {
  if (fileClasses.length === 0) return [];

  const groupingMap = fileClasses
    .filter(file => selectedFilePaths.has(file.filename))
    .flatMap(file => file.classes ?? [])
    .reduce((map, item) => {
      const existing = map.get(item.classId);
      if (existing) {
        existing.instances += item.instances;
      } else {
        map.set(item.classId, {
          classId: item.classId,
          instances: item.instances,
          level: getClassLevel(item.classId),
        });
      }
      return map;
    }, new Map<number, AnalysisClassPublicWithLevel>());

  return Array.from(groupingMap.values());
}

export function filterAndSortClasses(
  items: AnalysisClassPublicWithLevel[],
  selectedLevels: Level[],
  search: string,
  sort: Sorting,
  getTranslatedLabel: (classId: number) => string
): AnalysisClassPublicWithLevel[] {
  const searchLower = search.toLowerCase();

  const labeled: ClassWithLabel[] = items
    .filter(item => selectedLevels.includes(item.level))
    .map(item => ({ ...item, translatedLabel: getTranslatedLabel(item.classId) }))
    .filter(item => !searchLower || item.translatedLabel.toLowerCase().includes(searchLower));

  if (sort.direction === SortDirection.UNKNOWN || !sort.column) return labeled;

  const SORTABLE_COLUMNS: Set<string> = new Set<string>(['classId', 'level', 'instances']);
  if (!SORTABLE_COLUMNS.has(sort.column)) return labeled;

  const sorted = [...labeled];
  sorted.sort((a, b) => {
    let comparison = 0;
    if (sort.column === 'classId') {
      comparison = a.translatedLabel.localeCompare(b.translatedLabel);
    } else {
      const col = sort.column as keyof AnalysisClassPublicWithLevel;
      const valA = a[col] ?? 0;
      const valB = b[col] ?? 0;
      comparison = valA < valB ? -1 : valA > valB ? 1 : 0;
    }
    return sort.direction === SortDirection.ASC ? comparison : -comparison;
  });

  return sorted;
}
