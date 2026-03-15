import { apiClient, WS_BASE_URL } from './index';

// const isUUID = (value: string) =>
//     /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);

export async function startAndTrackLectureTask(
  file: File,
  onStatusChange?: (status: string) => void
): Promise<{ lectureId: string }> {
  
  console.log(`[FRONT] Starting upload for task ${file.name}`);
  const formData = new FormData();
  formData.append('file', file);

  const res = await apiClient.post(`/task/start`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  if (res.data.status?.toLowerCase() !== 'success') {
    throw new Error(res.data.msg || "Error start task");
  }

  console.log(`[FRONT] Task started successfully on backend`);

  return new Promise((resolve, reject) => {
    const ws = new WebSocket(`${WS_BASE_URL}/task/ws`);

    let isFinished = false;
    let isError = false;

    ws.onopen = () => {
      console.log(`[FRONT] WS open`);
    };

    ws.onmessage = (event) => {
      const msg = String(event.data);
      console.log('[WS message]', msg);

      if (isFinished) {
        ws.close();
        resolve({ lectureId: msg });
        return;
      }

      if (isError) {
        ws.close();
        reject(new Error(msg));
        return;
      }

      if (msg === "finish") {
        isFinished = true;
      } else if (msg === "error") {
        isError = true;
      } else {
        onStatusChange?.(msg);
      }
    };

    ws.onerror = (e) => {
      console.error(`[FRONT] WS Error`, e);
      ws.close();
      reject(e);
    };

    ws.onclose = () => console.log(`[FRONT] WS closed`);
  });
}

export async function getLectureResult(lectureId: string) {
  console.log(`[FRONT] Requesting result for lecture ${lectureId}`);
  const res = await apiClient.get(`/lectures/${lectureId}`);
  console.log(`[FRONT] Result received for lecture ${lectureId}`);
  return res.data;
}
