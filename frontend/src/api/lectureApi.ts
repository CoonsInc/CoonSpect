import { apiClient, WS_BASE_URL } from './index';

export async function createLectureTask() {
  console.log("[FRONT] Creating new lecture task...");
  const res = await apiClient.get('/create_task');
  console.log("[FRONT] Task created:", res.data);
  return res.data;
}

export async function uploadAudioViaWebSocket(
  file: File,
  taskId: number,
  onStatusChange?: (status: string) => void
) {
  console.log(`[FRONT] Connecting WS for task ${taskId}`);
  return new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`${WS_BASE_URL}/${taskId}`);

    ws.onopen = async () => {
      console.log(`[FRONT] WS open for task ${taskId}, sending file ${file.name}`);
      const reader = new FileReader();
      reader.onload = () => {
        const base64Data = (reader.result as string).split(',')[1];
        console.log(`[FRONT] File ${file.name} encoded (${base64Data.length} bytes)`);
        ws.send(JSON.stringify({
          type: 'file',
          filename: file.name,
          content: base64Data,
        }));
      };
      reader.readAsDataURL(file);
    };

    ws.onmessage = (event) => {
      const msg = event.data;
      console.log(`[FRONT] WS message (${taskId}):`, msg);
      onStatusChange?.(msg);
      if (msg === 'finish') {
        console.log(`[FRONT] WS task ${taskId} finished`);
        ws.close();
        resolve();
      }
    };

    ws.onerror = (err) => {
      console.error(`[FRONT] WS error (${taskId}):`, err);
      reject(err);
    };

    ws.onclose = (e) => {
      console.log(`[FRONT] WS closed (${taskId}), code=${e.code}, reason=${e.reason}`);
    };
  });
}

export async function getLectureResult(taskId: number) {
  console.log(`[FRONT] Requesting result for task ${taskId}`);
  const res = await apiClient.post(`/result/${taskId}`);
  console.log(`[FRONT] Result received for task ${taskId}:`, res.data);
  return res.data;
}
