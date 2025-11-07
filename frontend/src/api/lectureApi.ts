import { apiClient, WS_BASE_URL } from './index';

export async function createLectureTask() {
  const res = await apiClient.get('/create_task');
  return res.data;
}

export async function uploadAudioViaWebSocket(
  file: File,
  taskId: number,
  onStatusChange?: (status: string) => void
) {
  return new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`${WS_BASE_URL}/${taskId}`);

    ws.onopen = async () => {
      console.log('WebSocket connected');
      const reader = new FileReader();
      reader.onload = () => {
        const base64Data = (reader.result as string).split(',')[1];
        ws.send(
          JSON.stringify({
            type: 'file',
            filename: file.name,
            content: base64Data,
          })
        );
      };
      reader.readAsDataURL(file);
    };

    ws.onmessage = (event) => {
      const msg = event.data;
      console.log('WS message:', msg);
      onStatusChange?.(msg);

      if (msg === 'finish') {
        ws.close();
        resolve();
      }
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      reject(err);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };
  });
}

export async function getLectureResult(taskId: number) {
  const res = await apiClient.post(`/result/${taskId}`);
  return res.data;
}
