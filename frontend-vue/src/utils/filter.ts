import type { DateFilterValue, FilterEntity, FilterItem, FilterOptions, FilterValue } from '@/types/filter';
import { FilterType } from '@/types/filter';
import type { LocationQuery, LocationQueryValue } from 'vue-router';
import type { Primitive } from 'vuetify/lib/util';

// --- TYPE GUARDS ---

export function isDateFilterValue(val: any): val is DateFilterValue {
  return !!val && typeof val === 'object' && 'from' in val && 'to' in val;
}

export function isPrimitiveValue(val: any): val is Primitive {
  if (val === null) return true;

  const type = typeof val;
  return ['string', 'number', 'boolean', 'bigint', 'symbol'].includes(type);
}

export function isFilterEntity(val: any): val is FilterEntity {
  return !!val && typeof val === 'object' && typeof val.label === 'string' && isPrimitiveValue(val.value);
}

// --- MAIN FUNCTIONS ---

/**
 * Converts a specific filter value into a dictionary of URL parameters.
 */
export const serializeFilterValue = (filterItem: FilterItem, filterValue: FilterValue): Record<string, any> => {
  const value = filterValue[filterItem.key];

  if (value === undefined || value === null || value === '') return {};

  if (filterItem.serializer) return filterItem.serializer(filterValue);

  const urlKey = filterItem.query || filterItem.key;

  if (filterItem.type === FilterType.DATE) {
    if (!isDateFilterValue(value)) {
      console.error(`serializeDateFilterValue: Expected DateFilterValue for key '${urlKey}' but got ${typeof value}`);
      return {};
    }

    return serializeDateFilterValue(value, urlKey);
  }

  // Selects with 'return-object' (FilterEntity | FilterEntity[]) => Primitive or Primitive[]
  if (filterItem.options?.returnObject) {
    // This is FilterEntity or FilterEntity[] because the returnObject flag is set
    return serializeFilterEntity(value as FilterEntity | FilterEntity[], urlKey, filterItem.options.itemValue);
  }

  // Default Primitive
  return serializePrimitive(value as Primitive | Primitive[], urlKey);
};

/**
 * Reconstructs the complex UI value from the URL query parameters.
 */
export const deserializeFilterValue = (
  filterItem: FilterItem,
  query: LocationQuery
): Primitive | Primitive[] | FilterEntity | FilterEntity[] | DateFilterValue | undefined => {
  if (filterItem.deserializer) return filterItem.deserializer(query);

  const urlKey = filterItem.query || filterItem.key;

  if (filterItem.type === FilterType.DATE) {
    return deserializeDateFilterValue(query, urlKey);
  }

  // Standard Value
  const queryValue = query[urlKey];
  if (queryValue === undefined || queryValue === null) return undefined;

  return deserializeStandardValue(queryValue, filterItem);
};

// --- HELPERS (Internal) ---

/**
 * Helper to serialize date filter values into URL parameters using Epoch time.
 *
 * @param value The date filter value
 * @param key The key to use for the URL parameters.
 * @returns An object containing the serialized date filter values using Epoch time.
 */
function serializeDateFilterValue(value: DateFilterValue, key: string): Record<string, number | undefined> {
  return {
    [`${key}_from`]: value?.from ? value?.from?.getTime() : undefined,
    [`${key}_to`]: value?.to ? value?.to?.getTime() : undefined,
  };
}

function serializeFilterEntity(
  value: FilterEntity | FilterEntity[],
  key: string,
  valueKey: string = 'value'
): Record<string, Primitive | Primitive[]> {
  if (Array.isArray(value) && value.every(isFilterEntity)) {
    // FilterEntity[] => Primitive[]
    return { [key]: value.map(v => (typeof v === 'object' ? v[valueKey as keyof typeof v] : v)) };
  } else if (isFilterEntity(value)) {
    // FilterEntity => Primitive
    return { [key]: value[valueKey as keyof typeof value] };
  } else {
    console.error(`serializeFilterEntity: Expected object or array, got ${typeof value}`);
    return {};
  }
}

function serializePrimitive(value: Primitive | Primitive[], key: string): Record<string, Primitive | Primitive[]> {
  if (Array.isArray(value) && value.every(isPrimitiveValue)) {
    return { [key]: value };
  } else if (isPrimitiveValue(value)) {
    return { [key]: value };
  } else {
    console.error(`serializePrimitive: Expected primitive or array of primitives, got ${typeof value}`);
    return {};
  }
}

/**
 * Helper to deserialize date filter values from URL parameters using Epoch time.
 *
 * @param query The URL query parameters.
 * @param key The key to use for the URL parameters.
 * @returns The deserialized date filter value.
 */
function deserializeDateFilterValue(query: LocationQuery, key: string): DateFilterValue | undefined {
  const fromStr = query[`${key}_from`];
  const toStr = query[`${key}_to`];
  const result: DateFilterValue = {};

  if (fromStr) result.from = new Date(Number(fromStr));
  if (toStr) result.to = new Date(Number(toStr));

  // Only return if at least one date exists
  return result.from || result.to ? result : undefined;
}

/**
 * The "Brain" of deserialization.
 * * Logic:
 * 1. Normalize input to Array (handles Vue Router's string vs string[] inconsistency).
 * 2. If 'items' are provided, use them as a dictionary to recover original types (Boolean, BigInt, etc.)
 * or to find the original Entity object.
 * 3. Fallback to raw string or manual Number casting if no items match.
 * 4. Return either a single value or an array based on FilterType.
 *
 * Scenarios Matrix:
 * | URL Query   | Filter Type      | Options              | Items List          | Result (UI Model)    | Logic Applied                |
 * | :---------- | :--------------- | :------------------- | :------------------ | :------------------- | :--------------------------- |
 * | "pepe"      | SINGLE           | {}                   | []                  | "pepe"               | Raw String                   |
 * | "pepe"      | SELECT           | { returnObject: true }| [{l:'P', v:'pepe'}] | {l:'P', v:'pepe'}    | Entity Match                 |
 * | "pepe"      | MULTIPLE         | {}                   | []                  | ["pepe"]             | Normalized to Array          |
 * | "123"       | SINGLE           | { number: true }     | []                  | 123                  | Manual Number casting        |
 * | "123"       | SELECT           | {}                   | [100, 123, 200]     | 123                  | Type recovered from Items    |
 * | "true"      | SELECT           | {}                   | [true, false]       | true                 | Boolean recovered from Items |
 * | "900"       | SELECT           | {}                   | [900n, 100n]        | 900n                 | BigInt recovered from Items  |
 * | ["1", "2"]  | MULTIPLE         | { number: true }     | []                  | [1, 2]               | Array + Number casting       |
 * | "1"         | MULTIPLE_SELECT  | { returnObject: true }| [{l:'A', v:1}]      | [{l:'A', v:1}]       | Single URL -> Array[Object]  |
 * | "pepe"      | SELECT           | { returnObject: true }| [{l:'A', v:1}]      | "pepe"               | Mismatch -> Fallback to Raw  |
 * | null        | Any              | {}                   | Any                 | undefined            | Filter ignored               |
 */
function deserializeStandardValue(queryValue: LocationQueryValue | LocationQueryValue[], item: FilterItem): any {
  const { type, options = {} } = item;
  const isMultiple = [FilterType.MULTIPLE, FilterType.MULTIPLE_SELECT].includes(type);
  const valueKey = options.itemValue || 'value';

  // 1. NORMALIZE: Always work with an array internally to avoid "single string" bugs
  const rawValues = Array.isArray(queryValue) ? queryValue : [queryValue];
  const cleanValues = rawValues.filter((v): v is string => v !== null);

  // 2. MAPPING: Translate URL strings back to their original form
  const mappedValues = cleanValues.map(urlVal => {
    // Look for match in the items list (recovers Types and Objects)
    if (options.items && options.items.length > 0) {
      const match = options.items.find((it: any) => {
        // If it's an object, check the dynamic valueKey.
        // If it's a primitive, compare directly.
        const actualValue = it !== null && typeof it === 'object' ? it[valueKey] : it;
        return String(actualValue) === urlVal;
      });

      if (match !== undefined) {
        // If match found, return the full object or the typed value
        if (options.returnObject) return match;
        return isFilterEntity(match) ? match[valueKey as keyof typeof match] : match;
      }
    }

    // Fallback: If no match or no items, apply basic casting if requested
    if (options.number) {
      const num = Number(urlVal);
      return isNaN(num) ? urlVal : num;
    }

    return urlVal;
  });

  // Return array for multiple types, otherwise return the first element
  if (isMultiple) {
    return mappedValues;
  }

  return mappedValues.length > 0 ? mappedValues[0] : undefined;
}
