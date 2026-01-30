// Enums
export default class Enums {
  static buildList<T extends Record<string, any>>(enumObj: T): Array<{ value: keyof T; label: string }> {
    return Object.keys(enumObj)
      .filter(key => {
        const value = enumObj[key];
        return key !== '0' && key !== 'UNKNOWN' && value !== 0 && String(value).toUpperCase() !== 'UNKNOWN';
      })
      .map(key => ({
        value: key as keyof T,
        label: enumObj[key as keyof T],
      }));
  }
}
