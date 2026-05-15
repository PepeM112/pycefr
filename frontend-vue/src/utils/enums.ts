import { enumsLabels } from '@/messages';
import { type ComposerTranslation } from 'vue-i18n';

export type Enum = Record<string, string | number>;

export function isEnum(value: unknown): value is Enum {
  if (typeof value !== 'object' || value === null) return false;

  const values = Object.values(value);
  if (values.length === 0) return true;

  const typeOfFirstValue = typeof values[0];

  if (typeOfFirstValue !== 'string' && typeOfFirstValue !== 'number') return false;
  return values.every(v => typeof v === typeOfFirstValue);
}

interface BuildListOptions {
  sort?: boolean;
  labelTransform?: (label: string) => string;
  t?: ComposerTranslation;
}

export default class Enums {
  private static getLabelsByEnumType(enumType: Enum) {
    return enumsLabels.find(v => v.enum === enumType);
  }

  public static getValuesWithoutZero<T extends Enum>(enumType: T): T[keyof T][] {
    return Object.keys(enumType)
      .filter(key => isNaN(Number(key)))
      .map(key => enumType[key])
      .filter(
        (v): v is T[keyof T] =>
          (typeof v === 'number' && v !== 0) || (typeof v === 'string' && v.toLowerCase() !== 'unknown')
      );
  }

  public static getLabel<T extends Enum>(enumType: T, value: T[keyof T], t?: ComposerTranslation): string {
    const enumLabels = Enums.getLabelsByEnumType(enumType);

    if (enumLabels?.labels && value in enumLabels.labels) {
      const labelKey = enumLabels.labels[value as keyof typeof enumLabels.labels];
      if (labelKey) return t ? t(labelKey) : labelKey;
    }

    const fallback = enumType[value as keyof T];

    if (fallback !== undefined && fallback !== null) {
      return String(fallback);
    }

    return t ? t('unknown') : 'unknown';
  }

  public static buildList<T extends Enum>(
    enumType: T,
    options?: BuildListOptions
  ): Array<{ value: T[keyof T]; label: string }> {
    const t = options?.t;
    const values = Enums.getValuesWithoutZero(enumType);

    const list = values.map(value => ({
      value,
      label: options?.labelTransform
        ? options.labelTransform(Enums.getLabel(enumType, value, t))
        : Enums.getLabel(enumType, value, t),
    }));

    if (options?.sort !== false) {
      return list.sort((a, b) => a.label.localeCompare(b.label));
    }

    return list;
  }
}
