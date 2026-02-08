import { useI18n } from 'vue-i18n';

export const useRules = () => {
  const { t } = useI18n();

  const required = (v: any) => !!v || t('field_required');

  const url = (v: string) => {
    if (!v) return true;
    const pattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/;
    return pattern.test(v) || t('invalid_url_format');
  };

  const number = (v: any) => {
    if (v === null || v === undefined || v === '') return true;
    return !isNaN(Number(v)) || t('must_be_number');
  };

  const email = (v: string) => {
    if (!v) return true;
    const pattern =
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return pattern.test(v) || t('invalid_email');
  };

  return {
    required,
    url,
    number,
    email,
  };
};
