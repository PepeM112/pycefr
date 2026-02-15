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
  // 1. SERIALIZATION (App State -> URL Query)
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
        // LOGIC: 0 and false are legitimate filter values.
        const item = createItem({ key: 'k' });
        expect(serializeFilterValue(item, { k: 0 })).toEqual({ k: 0 });
        expect(serializeFilterValue(item, { k: false })).toEqual({ k: false });
      });

      it('should handle empty arrays by returning them as is', () => {
        // LOGIC: Verify that an empty array doesn't break serialization.
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
        // LOGIC: UI Date objects converted to Unix Timestamps.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const from = new Date('2023-01-01T00:00:00Z');
        const to = new Date('2023-01-02T00:00:00Z');
        expect(serializeFilterValue(item, { date: { from, to } })).toEqual({
          date_from: from.getTime(),
          date_to: to.getTime(),
        });
      });

      it('should return empty object for partial range (invalid case)', () => {
        // LOGIC: Strict rule -> Both dates must exist for the filter to be applied.
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const from = new Date('2023-01-01');
        expect(serializeFilterValue(item, { date: { from } as any })).toEqual({});
      });
    });

    describe('Entities and Objects (SELECT / MULTIPLE_SELECT)', () => {
      it('should extract the "value" property from an Entity', () => {
        // LOGIC: Standard entity serialization using default 'value' key.
        const item = createItem({ key: 'u', type: FilterType.SELECT, options: { returnObject: true } });
        const entity = { label: 'A', value: 1 };
        expect(serializeFilterValue(item, { u: entity } as any)).toEqual({ u: 1 });
      });

      it('should extract a custom property using "itemValue" option', () => {
        // LOGIC: Use 'id' instead of 'value' if specified in options.
        const item = createItem({
          key: 'u',
          type: FilterType.SELECT,
          options: { returnObject: true, itemValue: 'id' },
        });
        const entity = { label: 'A', id: 99, value: 'ignore' };
        expect(serializeFilterValue(item, { u: entity } as any)).toEqual({ u: 99 });
      });

      it('should serialize an array of entities into an array of values', () => {
        // LOGIC: Map multiple selected entities to their primitive values.
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
        const item = createItem({
          key: 'custom',
          serializer: val => ({ transformed: val.custom + '_OK' }),
        });
        expect(serializeFilterValue(item, { custom: 'data' })).toEqual({ transformed: 'data_OK' });
      });
    });
  });

  // =========================================================================
  // 2. DESERIALIZATION (URL Query -> App State)
  // =========================================================================
  describe('deserializeFilterValue', () => {
    describe('Basic Parsing and Normalization', () => {
      it('should return undefined if the key is missing from the query', () => {
        const item = createItem({ key: 'missing' });
        expect(deserializeFilterValue(item, {})).toBeUndefined();
      });

      it('should return the raw string if no options are provided', () => {
        const item = createItem({ key: 'q', type: FilterType.SINGLE });
        expect(deserializeFilterValue(item, { q: 'hello' })).toBe('hello');
      });

      it('should normalize a single URL string into an array for MULTIPLE types', () => {
        // LOGIC: Vue Router inconsistency fix (string vs string[]).
        const item = createItem({ key: 'tags', type: FilterType.MULTIPLE });
        expect(deserializeFilterValue(item, { tags: 'one' })).toEqual(['one']);
      });
    });

    describe('Casting and Type Recovery', () => {
      it('should cast strings to numbers when options.number is true', () => {
        const item = createItem({ key: 'n', type: FilterType.SINGLE, options: { number: true } });
        expect(deserializeFilterValue(item, { n: '123' })).toBe(123);
      });

      it('should return original string if number casting results in NaN', () => {
        const item = createItem({ key: 'n', type: FilterType.SINGLE, options: { number: true } });
        expect(deserializeFilterValue(item, { n: 'invalid' })).toBe('invalid');
      });

      it('should recover Boolean types from a list of items', () => {
        const item = createItem({ key: 'b', options: { items: [true, false] } });
        expect(deserializeFilterValue(item, { b: 'true' })).toBe(true);
        expect(deserializeFilterValue(item, { b: 'false' })).toBe(false);
      });

      it('should recover BigInt types from a list of items', () => {
        const big = 9007199254740991n;
        const item = createItem({ key: 'big', options: { items: [big] } });
        expect(deserializeFilterValue(item, { big: '9007199254740991' })).toBe(big);
      });

      it('should cast multiple values to numbers in an array', () => {
        const item = createItem({ key: 'nums', type: FilterType.MULTIPLE, options: { number: true } });
        expect(deserializeFilterValue(item, { nums: ['1', '2'] })).toEqual([1, 2]);
      });
    });

    describe('Object Reconstruction (returnObject)', () => {
      it('should find and return the full object from items based on URL value', () => {
        const obj = { label: 'Admin', value: 'adm' };
        const item = createItem({
          key: 'role',
          type: FilterType.SELECT,
          options: { returnObject: true, items: [obj] },
        });
        expect(deserializeFilterValue(item, { role: 'adm' })).toEqual(obj);
      });

      it('should find object using custom itemValue (e.g., code)', () => {
        const obj = { label: 'A', code: 'A1' };
        const item = createItem({
          key: 'x',
          options: { returnObject: true, itemValue: 'code', items: [obj as any] },
        });
        expect(deserializeFilterValue(item, { x: 'A1' })).toEqual(obj);
      });

      it('should return the raw value if no matching object is found in items', () => {
        const item = createItem({
          key: 'x',
          options: { returnObject: true, items: [{ label: 'A', value: 1 }] },
        });
        expect(deserializeFilterValue(item, { x: '999' })).toBe('999');
      });

      it('should return an array of objects for MULTIPLE_SELECT', () => {
        const obj1 = { label: 'A', value: 1 };
        const item = createItem({
          key: 'u',
          type: FilterType.MULTIPLE_SELECT,
          options: { returnObject: true, items: [obj1] },
        });
        expect(deserializeFilterValue(item, { u: '1' })).toEqual([obj1]);
      });
    });

    describe('Date Recovery', () => {
      it('should reconstruct a Date Range object from Epoch strings', () => {
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const epoch = 1672531200000;
        const result = deserializeFilterValue(item, { date_from: String(epoch) }) as any;
        expect(result.from).toBeInstanceOf(Date);
        expect(result.from.getTime()).toBe(epoch);
      });

      it('should handle full ranges (from and to)', () => {
        const item = createItem({ key: 'date', type: FilterType.DATE });
        const query = { date_from: '1000', date_to: '2000' };
        const result = deserializeFilterValue(item, query) as any;
        expect(result.from.getTime()).toBe(1000);
        expect(result.to.getTime()).toBe(2000);
      });
    });

    describe('Custom Behavior', () => {
      it('should use a custom deserializer if provided', () => {
        const item = createItem({
          key: 'custom',
          deserializer: q => q.custom + '_PARSED',
        });
        expect(deserializeFilterValue(item, { custom: 'raw' })).toBe('raw_PARSED');
      });
    });
  });

  // =========================================================================
  // 3. ROBUSTNESS & ERROR PATHS (Getting to 100%)
  // =========================================================================
  describe('Robustness and Error Handling', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    afterEach(() => {
      consoleSpy.mockClear();
    });

    it('should log error when serializePrimitive receives non-primitive data', () => {
      // LOGIC: Branch coverage for the default primitive serializer safety check.
      const item = createItem({ key: 'p' });
      const result = serializeFilterValue(item, { p: { nested: 'object' } } as any);
      expect(result).toEqual({});
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('serializePrimitive'));
    });

    it('should log error when serializeFilterEntity receives invalid entity data', () => {
      // LOGIC: Branch coverage for the entity serializer safety check.
      const item = createItem({ key: 'u', options: { returnObject: true } });
      const result = serializeFilterValue(item, { u: 'should-be-object' } as any);
      expect(result).toEqual({});
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('serializeFilterEntity'));
    });

    it('should log error when DATE type receives a non-date-range object', () => {
      // LOGIC: Branch coverage for the date-range type guard safety check.
      const item = createItem({ key: 'd', type: FilterType.DATE });
      const result = serializeFilterValue(item, { d: 'not-an-object' } as any);
      expect(result).toEqual({});
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('serializeDateFilterValue'));
    });

    it('should handle corrupt Date strings in URL gracefully', () => {
      // LOGIC: If URL contains "NaN" or text, new Date(NaN) returns "Invalid Date".
      const item = createItem({ key: 'd', type: FilterType.DATE });
      const result = deserializeFilterValue(item, { d_from: 'garbage' }) as any;
      expect(isNaN(result.from.getTime())).toBe(true);
    });
  });
});
