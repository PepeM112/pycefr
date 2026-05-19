import { deleteAnalysis } from '@/client';
import { useSnackbarStore } from '@/stores/snackbarStore';

export function useAnalysisDelete() {
  const snackbarStore = useSnackbarStore();

  async function removeAnalysis(id: number): Promise<boolean> {
    if (!id) return false;

    const { error } = await deleteAnalysis({
      path: { analysis_id: id },
    });

    if (error) {
      console.error('error.deleting.analysis:', error);
      snackbarStore.add({
        text: 'error.deleting.analysis',
        color: 'error',
        icon: 'mdi-alert-circle-outline',
        closable: true,
      });
      return false;
    }

    snackbarStore.add({
      text: 'success.deleting.analysis',
      color: 'success',
      icon: 'mdi-check-circle-outline',
      closable: true,
    });

    return true;
  }

  return { removeAnalysis };
}
