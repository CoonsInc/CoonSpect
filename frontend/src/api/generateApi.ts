import { apiClient, WS_BASE_URL } from './index';


export async function getLectureResult(lectureId: string) {
    console.log(`[FRONT] Requesting result for lecture ${lectureId}`);
    const res = await apiClient.get(`/lecture/${lectureId}`);
    console.log(`[FRONT] Result received for lecture ${lectureId}`);
    return res.data;
}

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

    let finalUploadUrl = upload_url;
    try {
        if (finalUploadUrl.startsWith('http')) {
            const urlObj = new URL(finalUploadUrl);
            finalUploadUrl = urlObj.pathname + urlObj.search;
        }
    } catch (e) {
        console.warn('Не удалось распарсить upload URL', e);
    }

    console.log(`[FRONT] Task initialized, starting direct S3 upload...`);
    onStatusChange?.("Загрузка файла на сервер...");

    try {
        const uploadRes = await fetch(finalUploadUrl, {
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

    return trackTaskViaWebSocket(onStatusChange);
}

export async function startAndTrackExampleTask(
    filename: string,
    onStatusChange?: (status: string) => void
): Promise<{ lectureId: string }> {
    console.log(`[FRONT] Requesting example task start for: ${filename}`);
    
    const res = await apiClient.post(`/task/example`, { 
        filename: filename 
    });

    const { task_id } = res.data; 
    if (!task_id) {
        throw new Error("Не удалось инициализировать задачу для примера");
    }

    console.log(`[FRONT] Example task ${task_id} initialized. Connecting to WS...`);
    onStatusChange?.("Инициализация примера...");

    return trackTaskViaWebSocket(onStatusChange);
}

function trackTaskViaWebSocket(
    onStatusChange?: (status: string) => void
): Promise<{ lectureId: string }> {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(`${WS_BASE_URL}/task/ws`);

        ws.onopen = () => console.log('[FRONT] WS open');

        ws.onmessage = (event) => {
            try {
                const { status, data } = JSON.parse(event.data);
                console.log('[WS message parsed]', { status, data });

                if (status === 'finish') {
                    ws.close();
                    resolve({ lectureId: String(data) });
                } else if (status === 'error') {
                    ws.close();
                    reject(new Error(String(data || 'Произошла ошибка при обработке')));
                } else {
                    onStatusChange?.(String(status));
                }
            } catch (err) {
                console.error('[FRONT] Failed to parse WS message:', event.data);
            }
        };

        ws.onerror = (e: Event) => {
            console.error('[FRONT] WS Error', e);
            ws.close();
            reject(new Error('Ошибка соединения с WebSocket'));
        };

        ws.onclose = () => console.log('[FRONT] WS closed');
    });
}
