<template>
  <v-menu v-model="showMenu" :close-on-content-click="false">
    <template #activator="{ props: menuProps }">
      <div v-bind="menuProps" class="d-flex align-center h-100 px-4" style="cursor: pointer">
        <span>{{ dateFilterValueToString(localDate) }}</span>
      </div>
    </template>
    <v-sheet class="pa-2" rounded="lg">
      <vue-date-picker
        v-model="datePickerDate"
        :key="isDark.toString()"
        range
        multi-calendars
        inline
        auto-apply
        :time-config="{ enableTimePicker: false }"
        :dark="isDark"
      />
      <div class="d-flex w-100 justify-end ga-2 pa-2 pb-0" style="border-top: 1px solid rgb(var(--v-theme-on-surface))">
        <v-btn variant="tonal" @click="showMenu = false">{{ $t('cancel') }}</v-btn>
        <v-btn color="primary-on-surface" variant="flat" @click="applyDate">{{ $t('apply') }}</v-btn>
      </div>
    </v-sheet>
  </v-menu>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue';
import { VueDatePicker } from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { useTheme } from 'vuetify';
import { type DateFilterValue } from '@/types/filter';
import { formatDate } from '@/utils/utils';
import dayjs from 'dayjs';

const emit = defineEmits<{
  (e: 'update:modelValue', value: DateFilterValue | undefined): void;
}>();

const theme = useTheme();

const props = withDefaults(
  defineProps<{
    modelValue: DateFilterValue | undefined;
  }>(),
  {
    modelValue: undefined,
  }
);

const showMenu = ref<boolean>(false);
const datePickerDate = ref<Date[] | undefined>(undefined);
const localDate = ref<DateFilterValue | undefined>(undefined);

const isDark = computed(() => theme.global.current.value.dark);

function applyDate() {
  showMenu.value = false;
  localDate.value = datesToDateFilterValue(datePickerDate.value);
  emit('update:modelValue', localDate.value);
}

function datesToDateFilterValue(dates: Date[] | undefined): DateFilterValue | undefined {
  if (!dates) return undefined;
  const from = dayjs(dates[0]).startOf('day').toDate();
  const to = dayjs(dates[1]).endOf('day').toDate();
  return { from, to };
}

function dateFilterValueToString(date: DateFilterValue | undefined): string {
  if (!date) return '';
  const from = date.from ? formatDate(date.from, 'DD-MM-YYYY HH:mm:ss') : '';
  const to = date.to ? formatDate(date.to, 'DD-MM-YYYY HH:mm:ss') : '';
  return from && to ? `${from} - ${to}` : from || to;
}
</script>
<style lang="scss" scoped>
:deep(.dp__menu) {
  border: unset;
}
:deep(.dp__theme_dark) {
  --dp-background-color: rgb(var(--v-theme-primary));
}
</style>
