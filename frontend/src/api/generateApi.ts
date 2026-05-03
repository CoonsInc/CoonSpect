import { apiClient, WS_BASE_URL } from './index';

export async function startAndTrackLectureTask(
    file: File,
    onStatusChange?: (status: string) => void
): Promise<{ lectureId: string }> {
  
    console.log(`[FRONT] Requesting upload URL for task ${file.name}`);
    
    const res = await apiClient.post(`/task/start`, { 
        filename: file.name 
    });

    const { upload_url } = res.data;

    if (!upload_url) {
        throw new Error("Не удалось получить URL для загрузки файла");
    }

    console.log(`[FRONT] Task initialized, starting direct S3 upload...`);
    onStatusChange?.("Загрузка файла на сервер...");

    try {
        const uploadRes = await fetch(upload_url, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': 'audio/mpeg' 
            }
        });

        if (!uploadRes.ok) {
            throw new Error(`Ошибка загрузки в S3: ${uploadRes.status} ${uploadRes.statusText}`);
        }

        await apiClient.post(`/task/confirm`);

    } catch (err) {
        console.error(`[FRONT] S3 Upload failed:`, err);
        throw err;
    }

    console.log(`[FRONT] File uploaded to S3 successfully. Connecting to WS...`);
    onStatusChange?.("Файл загружен. Ожидание обработки...");

    return new Promise((resolve, reject) => {
        const ws = new WebSocket(`${WS_BASE_URL}/task/ws`);

        ws.onopen = () => console.log(`[FRONT] WS open`);

        ws.onmessage = (event) => {
            try {
                const { status, data } = JSON.parse(event.data);
                console.log('[WS message parsed]', { status, data });

                if (status === "finish") {
                    ws.close();
                    resolve({ lectureId: String(data) }); 
                } 
                else if (status === "error") {
                    ws.close();
                    reject(new Error(String(data || "Произошла ошибка при обработке")));
                } 
                else {
                    onStatusChange?.(String(status));
                }
            } catch (err) {
                console.error(`[FRONT] Failed to parse WS message:`, event.data);
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
    const res = await apiClient.get(`/lecture/${lectureId}`);
    console.log(`[FRONT] Result received for lecture ${lectureId}`);
    return res.data;
}
