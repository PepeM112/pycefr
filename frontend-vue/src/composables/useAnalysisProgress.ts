import { ref, onUnmounted, readonly } from 'vue';
import { client } from '@/client/client.gen';

export type AnalysisStep = 'VALIDATING' | 'CLONING' | 'ANALYSING' | 'GIT_ANALYSIS' | 'SAVING' | 'COMPLETED' | 'FAILED';

type ProgressEvent = {
  step: AnalysisStep;
  current?: number;
  total?: number;
  analysisId?: number;
  error?: string;
};

export function useAnalysisProgress() {
  const currentStep = ref<AnalysisStep | null>(null);
  const fileCurrent = ref(0);
  const fileTotal = ref(0);
  const errorMessage = ref<string | null>(null);
  const isTerminal = ref(false);
  const completedAnalysisId = ref<number | null>(null);

  let eventSource: EventSource | null = null;

  function connect(analysisId: number) {
    disconnect();
    isTerminal.value = false;
    currentStep.value = null;
    fileCurrent.value = 0;
    fileTotal.value = 0;
    errorMessage.value = null;
    completedAnalysisId.value = null;

    const baseUrl = client.getConfig().baseUrl ?? '';
    eventSource = new EventSource(`${baseUrl}/api/v1/analyses/${analysisId}/progress`);

    eventSource.onmessage = (event: MessageEvent) => {
      const data: ProgressEvent = JSON.parse(event.data);
      currentStep.value = data.step;

      if (data.step === 'ANALYSING' && data.total !== undefined) {
        fileCurrent.value = data.current ?? 0;
        fileTotal.value = data.total;
      }

      if (data.step === 'COMPLETED') {
        completedAnalysisId.value = data.analysisId ?? null;
        isTerminal.value = true;
        disconnect();
      }

      if (data.step === 'FAILED') {
        errorMessage.value = data.error ?? null;
        isTerminal.value = true;
        disconnect();
      }
    };

    eventSource.onerror = () => {
      if (!isTerminal.value) {
        errorMessage.value = 'Connection to server lost.';
        currentStep.value = 'FAILED';
        isTerminal.value = true;
      }
      disconnect();
    };
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  onUnmounted(disconnect);

  return {
    currentStep: readonly(currentStep),
    fileCurrent: readonly(fileCurrent),
    fileTotal: readonly(fileTotal),
    errorMessage: readonly(errorMessage),
    isTerminal: readonly(isTerminal),
    completedAnalysisId: readonly(completedAnalysisId),
    connect,
    disconnect,
  };
}
