import { type ComposerTranslation } from 'vue-i18n';
import { enumsLabels } from '@/messages';

export type Enum = Record<string, string | number>;

type BuildListOptions = {
  sort?: boolean;
  labelTransform?: (label: string) => string;
  t?: ComposerTranslation;
};

function getLabelsByEnumType(enumType: Enum) {
  return enumsLabels.find(v => v.enum === enumType);
}

export function getValuesWithoutZero<V extends string | number, T extends Record<string, V>>(enumType: T): V[] {
  return Object.keys(enumType)
    .filter(key => isNaN(Number(key)))
    .map(key => enumType[key])
    .filter(
      (v): v is V => (typeof v === 'number' && v !== 0) || (typeof v === 'string' && v.toLowerCase() !== 'unknown')
    );
}

export function getLabel<V extends string | number, T extends Record<string, V>>(
  enumType: T,
  value: V,
  t?: ComposerTranslation
): string {
  const enumLabels = getLabelsByEnumType(enumType);

  if (enumLabels?.labels && value in enumLabels.labels) {
    const labelKey = enumLabels.labels[value];
    if (labelKey) return t ? t(labelKey) : labelKey;
  }

  const fallback = enumType[value as unknown as keyof T];

  if (fallback !== undefined && fallback !== null) {
    return String(fallback);
  }

  return t ? t('unknown') : 'unknown';
}

export function buildList<V extends string | number, T extends Record<string, V>>(
  enumType: T,
  options?: BuildListOptions
): Array<{ value: V; label: string }> {
  const t = options?.t;
  const values = getValuesWithoutZero(enumType);

  const list = values.map(value => ({
    value,
    label: options?.labelTransform
      ? options.labelTransform(getLabel(enumType, value, t))
      : getLabel(enumType, value, t),
  }));

  if (options?.sort !== false) {
    return list.sort((a, b) => a.label.localeCompare(b.label));
  }

  return list;
}
