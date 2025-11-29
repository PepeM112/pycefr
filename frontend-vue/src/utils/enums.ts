// Enums
export default class Enums {
  static buildList<T extends Record<string, any>>(enumObj: T): Array<{ value: keyof T; label: string }> {
    return Object.keys(enumObj).map(key => ({
      value: key as keyof T,
      label: enumObj[key as keyof T],
    }));
  }
}
