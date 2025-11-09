import { apiClient, WS_BASE_URL } from './index';

export async function createLectureTask() {
  console.log("[FRONT] Creating new lecture task...");
  const res = await apiClient.get('/create_task');
  console.log("[FRONT] Task created:", res.data);
  return res.data;
}

export async function uploadAudioViaHTTP(
  file: File,
  taskId: number,
  onStatusChange?: (status: string) => void
) {
  console.log(`[FRONT] Starting upload for task ${taskId}`);
  return new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`${WS_BASE_URL}/${taskId}`);

    ws.onopen = async () => {
      console.log(`[FRONT] WS open for task ${taskId}`);

      const formData = new FormData();
      formData.append("file", file);

      try {
        await apiClient.post(`/upload_audio/${taskId}`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (e) => {
            const percent = Math.round((e.loaded / (e.total || 1)) * 100);
            onStatusChange?.(`uploading ${percent}%`);
          },
        });
        console.log(`[FRONT] Upload finished, waiting for STT...`);
      } catch (err) {
        console.error(`[FRONT] Upload failed:`, err);
        reject(err);
      }
    };

    ws.onmessage = (event) => {
      const msg = event.data;
      console.log(`[FRONT] WS message (${taskId}):`, msg);
      onStatusChange?.(msg);

      if (msg === "finish") {
        console.log(`[FRONT] WS task ${taskId} finished`);
        ws.close();
        resolve();
      }
    };

    ws.onerror = (err) => {
      console.error(`[FRONT] WS error (${taskId}):`, err);
      reject(err);
    };

    ws.onclose = () => console.log(`[FRONT] WS closed (${taskId})`);
  });
}

export async function getLectureResult(taskId: number) {
  console.log(`[FRONT] Requesting result for task ${taskId}`);
  const res = await apiClient.post(`/result/${taskId}`);
  console.log(`[FRONT] Result received for task ${taskId}:`, res.data);
  return res.data;
}
