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
  if (
    (filterItem.type === FilterType.SELECT || filterItem.type === FilterType.MULTIPLE_SELECT) &&
    filterItem.options?.returnObject
  ) {
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

  return deserializeStandardValue(queryValue, filterItem.options);
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

function deserializeStandardValue(
  queryValue: LocationQueryValue | LocationQueryValue[],
  filterOptions: FilterOptions = {}
): Primitive | Primitive[] | FilterEntity | FilterEntity[] | undefined {
  const items = filterOptions.items;
  const valueKey = filterOptions.itemValue || 'value';

  const findFilterEntityItem = (queryVal: LocationQueryValue): FilterEntity | undefined => {
    if (queryVal === null || queryVal === undefined || !items) return undefined;
    if (!items.every(isFilterEntity)) {
      console.error(`deserializeStandardValue: Expected items to be FilterEntity[] but got a different type`);
      return undefined;
    }
    return items.find(it => {
      const entityVal = it[valueKey as keyof typeof it];
      if (!entityVal) {
        console.error(`deserializeStandardValue: Item is missing the value key '${valueKey}'`);
        return undefined;
      }
      return String(entityVal) === queryVal;
    });
  };

  const findPrimitiveItem = (queryVal: LocationQueryValue): Primitive | undefined => {
    if (queryVal === null || queryVal === undefined || !items) return undefined;
    if (!items.every(isPrimitiveValue)) {
      console.error(`deserializeStandardValue: Expected items to be Primitive[] but got a different type`);
      return undefined;
    }
    return items.find(it => String(it) === queryVal);
  };

  if (filterOptions.returnObject) {
    // We expect FilterEntity or FilterEntity[]
    if (!items) {
      // Items are always required with FilterEntity
      console.error(`deserializeStandardValue: returnObject is true but items are undefined`);
      return undefined;
    }

    if (!items.every(isFilterEntity)) {
      console.error(`deserializeStandardValue: returnObject is true but some items are not FilterEntity`);
      return undefined;
    }

    if (Array.isArray(queryValue)) {
      const result = queryValue.map(findFilterEntityItem);
      if (!result.every(isFilterEntity)) {
        console.error(`deserializeStandardValue: Some query values did not match any FilterEntity`);
        return undefined;
      }
      return result.length > 0 ? result : undefined;
    }

    return findFilterEntityItem(queryValue) as FilterEntity | undefined;
  } else {
    // We expect Primitive or Primitive[]
    if (items) {
      // If items are provided, they must be Primitive to match the expected return type
      if (!items.every(isPrimitiveValue)) {
        console.error(`deserializeStandardValue: returnObject is false but some items are not Primitive`);
        return undefined;
      }

      if (Array.isArray(queryValue)) {
        const result = queryValue.map(findPrimitiveItem);
        if (!result.every(isPrimitiveValue)) {
          console.error(`deserializeStandardValue: Some query values did not match any Primitive`);
          return undefined;
        }
        return result.length > 0 ? result : undefined;
      }
      return findPrimitiveItem(queryValue) as Primitive | undefined;
    } else {
      // No items provided, just return the raw query value as Primitive or Primitive[]
      if (Array.isArray(queryValue)) {
        const result = queryValue.filter(v => v !== null && v !== undefined);
        return filterOptions?.number ? result.map(Number) : (result as Primitive[]);
      }
      return filterOptions?.number ? Number(queryValue) : (queryValue as Primitive);
    }
  }
}
