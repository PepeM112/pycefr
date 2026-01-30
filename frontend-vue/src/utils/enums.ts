import { enumsLabels } from '@/messages';
import { type ComposerTranslation } from 'vue-i18n';

interface BuildListOptions {
  sort?: boolean;
  labelTransform?: (label: string) => string;
  t?: ComposerTranslation;
}

export default class Enums {
  private static getLabelsByEnumType(enumType: any) {
    return enumsLabels.find(v => v.enum === enumType);
  }

  public static getLabel<T extends Record<string, any>>(enumType: T, value: any, t?: ComposerTranslation): string {
    const enumLabels = Enums.getLabelsByEnumType(enumType);

    if (enumLabels?.labels && value in enumLabels.labels) {
      const labelKey = enumLabels.labels[value as keyof typeof enumLabels.labels];
      return t ? t(labelKey) : labelKey;
    }

    const fallback = enumType[value] ?? value;

    if (fallback !== undefined && fallback !== null) {
      return String(fallback);
    }

    return t ? t('unknown') : 'unknown';
  }

  public static getValuesWithoutZero(enumType: any): (number | string)[] {
    return Object.keys(enumType).filter(key => {
      const value = enumType[key];
      // Exclude keys and values '0' and 'UNKNOWN'
      return (
        key !== '0' && key !== '_0' && key !== 'UNKNOWN' && value !== 0 && String(value).toUpperCase() !== 'UNKNOWN'
      );
    });
  }

  public static buildList<T extends Record<string, any>>(
    enumType: T,
    options?: BuildListOptions
  ): Array<{ value: any; label: string }> {
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
