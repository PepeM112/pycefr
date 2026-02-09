import { ref } from 'vue';
import { defineStore } from 'pinia';

export interface SnackbarOptions {
  text: string;
  title?: string;
  color?: string;
  timeout?: number;
  closable?: boolean;
  icon?: string;
  closeIcon?: string;
  onClick?: () => void;
}

interface SnackbarMessage extends SnackbarOptions {
  id: number;
  show: boolean;
}

const DEFAULT_OPTIONS: Partial<SnackbarMessage> = {
  color: 'success',
  timeout: 4000,
  closable: true,
  closeIcon: 'mdi-close',
};

export const useSnackbarStore = defineStore('snackbar', () => {
  const messages = ref<SnackbarMessage[]>([]);
  let nextId = 0;

  function add(options: SnackbarOptions) {
    const id = nextId++;

    const newMessage: SnackbarMessage = {
      ...DEFAULT_OPTIONS,
      ...options,
      id,
      show: true,
    };

    messages.value.unshift(newMessage);

    if (messages.value.length > 5) {
      messages.value.pop();
    }

    if (newMessage.timeout && newMessage.timeout > 0) {
      setTimeout(() => remove(id), newMessage.timeout);
    }
  }

  function remove(id: number) {
    const index = messages.value.findIndex(m => m.id === id);
    if (index !== -1) {
      messages.value.splice(index, 1);
    }
  }

  function clear() {
    messages.value = [];
  }

  return { messages, add, remove, clear };
});
