import { FilterType, type FilterItem } from '@/types/filter';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { deserializeFilterValue, serializeFilterValue } from '../filter';

/**
 * HELPER: createItem
 * Utility to quickly generate a FilterItem for testing purposes.
 */
const createItem = (overrides: Partial<FilterItem>): FilterItem =>
  ({
    label: 'Test',
    key: 'testKey',
    type: FilterType.SINGLE,
    ...overrides,
  }) as FilterItem;

describe('utils/filter.ts', () => {
  // =========================================================================
  // SERIALIZATION (App State -> URL Query)
  // =========================================================================
  describe('serializeFilterValue', () => {
    describe('Empty and Falsy Values', () => {
      it('should return empty object for null, undefined, or empty string', () => {
        // LOGIC: Avoid polluting the URL with empty or non-existent values.
        const item = createItem({ key: 'k' });
        expect(serializeFilterValue(item, { k: null } as any)).toEqual({});
        expect(serializeFilterValue(item, { k: undefined } as any)).toEqual({});
        expect(serializeFilterValue(item, { k: '' })).toEqual({});
      });

      it('should NOT return empty object for 0 or false', () => {
        // LOGIC: Maintain semantic falsy values (0, false) as they are valid filters.
        const item = createItem({ key: 'k' });
        expect(serializeFilterValue(item, { k: 0 })).toEqual({ k: 0 });
        expect(serializeFilterValue(item, { k: false })).toEqual({ k: false });
      });

      it('should handle empty arrays by returning them as is', () => {
        // LOGIC: Ensure empty arrays are preserved for filters that expect list structures.
        const item = createItem({ key: 'tags', type: FilterType.MULTIPLE });
        expect(serializeFilterValue(item, { tags: [] })).toEqual({ tags: [] });
      });
    });

    describe('Primitive Types', () => {
      it('should serialize Single Primitives', () => {
        // INPUT: { status: 'active' } -> EXPECT: { status: 'active' }
        const item = createItem({ key: 'status', type: FilterType.SINGLE });
        expect(serializeFilterValue(item, { status: 'active' })).toEqual({ status: 'active' });
      });

      it('should serialize Multiple Primitives', () => {
        // INPUT: { tags: ['a', 'b'] } -> EXPECT: { tags: ['a', 'b'] }
        const item = createItem({ key: 'tags', type: FilterType.MULTIPLE });
        expect(serializeFilterValue(item, { tags: ['a', 'b'] })).toEqual({ tags: ['a', 'b'] });
      });
    });

    describe('Date Range (FilterType.DATE)', () => {
      it('should serialize valid Date Range to Epoch numbers', () => {
        // LOGIC: Convert UI Date objects to Unix Timestamps for URL compatibility.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const from = new Date('2023-01-01T00:00:00Z');
        const to = new Date('2023-01-02T00:00:00Z');
        expect(serializeFilterValue(item, { date: { from, to } })).toEqual({
          date_from: from.getTime(),
          date_to: to.getTime(),
        });
      });

      it('should return empty object for partial range (invalid case)', () => {
        // LOGIC: If a required property is missing from the object, ignore the filter.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const from = new Date('2023-01-01');
        expect(serializeFilterValue(item, { date: { from } as any })).toEqual({});
      });

      it('should serialize partial date ranges if keys exist but are null', () => {
        // LOGIC: Allow serialization of partial ranges if keys are explicitly present as null.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const from = new Date('2023-01-01');
        const result = serializeFilterValue(item, { date: { from, to: null } as any });

        expect(result).toEqual({
          date_from: from.getTime(),
          date_to: undefined,
        });
      });
    });

    describe('Entities and Objects (SELECT / MULTIPLE_SELECT)', () => {
      it('should extract the "value" property from an Entity', () => {
        // LOGIC: Map full UI objects to their primitive IDs for URL storage.
        const item = createItem({ key: 'u', type: FilterType.SELECT, options: { returnObject: true } });
        const entity = { label: 'A', value: 1 };
        expect(serializeFilterValue(item, { u: entity } as any)).toEqual({ u: 1 });
      });

      it('should serialize an array of entities into an array of values', () => {
        // LOGIC: Flatten multiple selected entity objects into an array of primitive values.
        const item = createItem({ key: 'u', type: FilterType.MULTIPLE_SELECT, options: { returnObject: true } });
        const entities = [
          { label: 'A', value: 1 },
          { label: 'B', value: 2 },
        ];
        expect(serializeFilterValue(item, { u: entities } as any)).toEqual({ u: [1, 2] });
      });
    });

    describe('Custom Behavior', () => {
      it('should use a custom serializer if provided in the item configuration', () => {
        // LOGIC: Override default logic with user-defined serialization functions.
        const item = createItem({
          key: 'custom',
          serializer: val => ({ transformed: val.custom + '_OK' }),
        });
        expect(serializeFilterValue(item, { custom: 'data' })).toEqual({ transformed: 'data_OK' });
      });
    });
  });

  // =========================================================================
  // DESERIALIZATION (URL Query -> App State)
  // =========================================================================
  describe('deserializeFilterValue', () => {
    describe('Basic Parsing and Normalization', () => {
      it('should return undefined if the key is missing from the query', () => {
        // LOGIC: Return undefined for missing parameters to allow for default state.
        const item = createItem({ key: 'missing' });
        expect(deserializeFilterValue(item, {})).toBeUndefined();
      });

      it('should return the raw string if no options are provided', () => {
        // LOGIC: Pass-through strings as the simplest form of filter value.
        const item = createItem({ key: 'q', type: FilterType.SINGLE });
        expect(deserializeFilterValue(item, { q: 'hello' })).toBe('hello');
      });

      it('should normalize a single URL string into an array for MULTIPLE types', () => {
        // LOGIC: Ensure consistency regardless of whether Vue Router returns string or string[].
        const item = createItem({ key: 'tags', type: FilterType.MULTIPLE });
        expect(deserializeFilterValue(item, { tags: 'one' })).toEqual(['one']);
      });

      it('should filter out null values from a query array', () => {
        // LOGIC: Cleanse incoming URL arrays from null/empty values to maintain data integrity.
        const item = createItem({ key: 'tags', type: FilterType.MULTIPLE });
        expect(deserializeFilterValue(item, { tags: ['one', null, 'two'] as any })).toEqual(['one', 'two']);
      });
    });

    describe('Casting and Type Recovery', () => {
      it('should cast strings to numbers when options.number is true', () => {
        // LOGIC: Explicitly convert numeric URL strings back to Javascript Numbers.
        const item = createItem({ key: 'n', type: FilterType.SINGLE, options: { number: true } });
        expect(deserializeFilterValue(item, { n: '123' })).toBe(123);
      });

      it('should return original string if number casting results in NaN', () => {
        // LOGIC: Fallback to raw string if casting fails to prevent data loss.
        const item = createItem({ key: 'n', type: FilterType.SINGLE, options: { number: true } });
        expect(deserializeFilterValue(item, { n: 'invalid' })).toBe('invalid');
      });

      it('should recover Boolean types from a list of items', () => {
        // LOGIC: Restore native Booleans from URL strings by matching against available options.
        const item = createItem({ key: 'b', options: { items: [true, false] } });
        expect(deserializeFilterValue(item, { b: 'true' })).toBe(true);
        expect(deserializeFilterValue(item, { b: 'false' })).toBe(false);
      });

      it('should recover BigInt types from a list of items', () => {
        // LOGIC: Handle large numeric IDs by matching URL strings against BigInt items.
        const big = 9007199254740991n;
        const item = createItem({ key: 'big', options: { items: [big] } });
        expect(deserializeFilterValue(item, { big: '9007199254740991' })).toBe(big);
      });

      it('should cast multiple values to numbers in an array', () => {
        // LOGIC: Apply numeric casting across all elements in a multi-value filter.
        const item = createItem({ key: 'nums', type: FilterType.MULTIPLE, options: { number: true } });
        expect(deserializeFilterValue(item, { nums: ['1', '2'] })).toEqual([1, 2]);
      });

      it('should recover a Number type from items list match', () => {
        // LOGIC: Recover native Number type even without explicit number:true flag by matching options.
        const item = createItem({ key: 'id', options: { items: [100, 200] } });
        expect(deserializeFilterValue(item, { id: '200' })).toBe(200);
      });
    });

    describe('Object Reconstruction (returnObject)', () => {
      it('should find and return the full object from items based on URL value', () => {
        // LOGIC: Rehydrate the full UI object from a primitive ID using the items registry.
        const obj = { label: 'Admin', value: 'adm' };
        const item = createItem({
          key: 'role',
          type: FilterType.SELECT,
          options: { returnObject: true, items: [obj] },
        });
        expect(deserializeFilterValue(item, { role: 'adm' })).toEqual(obj);
      });

      it('should return the raw value if no matching object is found in items', () => {
        // LOGIC: Gracefully handle cases where the URL value doesn't exist in the current items list.
        const item = createItem({
          key: 'x',
          options: { returnObject: true, items: [{ label: 'A', value: 1 }] },
        });
        expect(deserializeFilterValue(item, { x: '999' })).toBe('999');
      });

      it('should return an array of objects for MULTIPLE_SELECT', () => {
        // LOGIC: Reconstruct an array of UI entities from a single or multiple URL IDs.
        const obj1 = { label: 'A', value: 1 };
        const item = createItem({
          key: 'u',
          type: FilterType.MULTIPLE_SELECT,
          options: { returnObject: true, items: [obj1] },
        });
        expect(deserializeFilterValue(item, { u: '1' })).toEqual([obj1]);
      });

      it('should return raw string on mismatch even if returnObject is true', () => {
        // LOGIC: Ensure the logic doesn't crash if an ID from the URL is not found in the options list.
        const item = createItem({
          key: 'role',
          options: { returnObject: true, items: [{ label: 'Admin', value: 'admin' }] },
        });
        expect(deserializeFilterValue(item, { role: 'user' })).toBe('user');
      });
    });

    describe('Date Recovery', () => {
      it('should reconstruct a Date Range object from Epoch strings', () => {
        // LOGIC: Parse numeric URL strings into native Javascript Date objects.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const epoch = 1672531200000;
        const result = deserializeFilterValue(item, { date_from: String(epoch) }) as any;
        expect(result.from).toBeInstanceOf(Date);
        expect(result.from.getTime()).toBe(epoch);
      });

      it('should handle full ranges (from and to)', () => {
        // LOGIC: Map separated URL date parameters back into a unified DateFilterValue object.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const query = { date_from: '1000', date_to: '2000' };
        const result = deserializeFilterValue(item, query) as any;
        expect(result.from.getTime()).toBe(1000);
        expect(result.to.getTime()).toBe(2000);
      });
    });

    describe('Custom Behavior', () => {
      it('should use a custom deserializer if provided', () => {
        // LOGIC: Use provided transformation logic for specialized URL-to-state parsing.
        const item = createItem({
          key: 'custom',
          deserializer: q => q.custom + '_PARSED',
        });
        expect(deserializeFilterValue(item, { custom: 'raw' })).toBe('raw_PARSED');
      });
    });
  });

  // =========================================================================
  // ROBUSTNESS & ERROR PATHS (Safety Check Branch Coverage)
  // =========================================================================
  describe('Robustness and Error Handling', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    afterEach(() => {
      consoleSpy.mockClear();
    });

    it('should log error when serializePrimitive receives non-primitive data', () => {
      // LOGIC: Ensure the default serializer catches and reports unexpected object structures.
      const item = createItem({ key: 'p' });
      const result = serializeFilterValue(item, { p: { nested: 'object' } } as any);
      expect(result).toEqual({});
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('serializePrimitive'));
    });

    it('should log error when serializeFilterEntity receives invalid entity data', () => {
      // LOGIC: Validate that entity serialization requires a proper object structure.
      const item = createItem({ key: 'u', options: { returnObject: true } });
      const result = serializeFilterValue(item, { u: 'should-be-object' } as any);
      expect(result).toEqual({});
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('serializeFilterEntity'));
    });

    it('should log error when DATE type receives a non-date-range object', () => {
      // LOGIC: Enforce strict type checking for the DATE filter type during serialization.
      const item = createItem({ key: 'd', type: FilterType.DATE });
      const result = serializeFilterValue(item, { d: 'not-an-object' } as any);
      expect(result).toEqual({});
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('serializeDateFilterValue'));
    });

    it('should handle corrupt Date strings in URL gracefully', () => {
      // LOGIC: Robust parsing for malformed URL date strings to prevent application crashes.
      const item = createItem({ key: 'd', type: FilterType.DATE });
      const result = deserializeFilterValue(item, { d_from: 'garbage' }) as any;
      expect(isNaN(result.from.getTime())).toBe(true);
    });
  });
});
