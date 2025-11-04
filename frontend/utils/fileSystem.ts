export interface SaveFileResult {
  success: boolean;
  path?: string;
  error?: string;
}

export class FileSystemManager {
  private static readonly DB_NAME = 'CoonSpectDB';
  private static readonly STORE_NAME = 'audioFiles';
  private static readonly DB_VERSION = 1;

  /**
   * Инициализирует IndexedDB
   */
  private static async initDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          const store = db.createObjectStore(this.STORE_NAME, { keyPath: 'id' });
          store.createIndex('fileName', 'fileName', { unique: false });
          store.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  /**
   * Сохраняет файл в IndexedDB
   */
  static async saveFileToDisk(file: File, folderName: string = 'downloads'): Promise<SaveFileResult> {
    try {
      const db = await this.initDB();
      const fileName = this.generateFileName(file.name);
      const fileData = {
        id: `${folderName}/${fileName}`,
        fileName,
        folderName,
        originalName: file.name,
        file: file,
        timestamp: new Date().toISOString(),
        size: file.size,
        type: file.type
      };

      return new Promise((resolve) => {
        const transaction = db.transaction([this.STORE_NAME], 'readwrite');
        const store = transaction.objectStore(this.STORE_NAME);
        const request = store.put(fileData);

        request.onsuccess = () => {
          console.log('✅ Файл успешно сохранен в IndexedDB:', fileData.id);
          resolve({
            success: true,
            path: fileData.id
          });
        };

        request.onerror = () => {
          console.error('❌ Ошибка сохранения в IndexedDB:', request.error);
          resolve({
            success: false,
            error: 'Failed to save file to IndexedDB'
          });
        };
      });
    } catch (error) {
      console.error('Error saving file to IndexedDB:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получает файл из IndexedDB
   */
  static async getFile(fileId: string): Promise<File | null> {
    try {
      const db = await this.initDB();
      return new Promise((resolve) => {
        const transaction = db.transaction([this.STORE_NAME], 'readonly');
        const store = transaction.objectStore(this.STORE_NAME);
        const request = store.get(fileId);

        request.onsuccess = () => {
          const fileData = request.result;
          resolve(fileData ? fileData.file : null);
        };

        request.onerror = () => {
          console.error('❌ Ошибка получения файла из IndexedDB:', request.error);
          resolve(null);
        };
      });
    } catch (error) {
      console.error('Error getting file from IndexedDB:', error);
      return null;
    }
  }

  /**
   * Получает список всех сохраненных файлов
   */
  static async getAllFiles(): Promise<any[]> {
    try {
      const db = await this.initDB();
      return new Promise((resolve) => {
        const transaction = db.transaction([this.STORE_NAME], 'readonly');
        const store = transaction.objectStore(this.STORE_NAME);
        const request = store.getAll();

        request.onsuccess = () => {
          resolve(request.result || []);
        };

        request.onerror = () => {
          console.error('❌ Ошибка получения списка файлов:', request.error);
          resolve([]);
        };
      });
    } catch (error) {
      console.error('Error getting all files from IndexedDB:', error);
      return [];
    }
  }

  /**
   * Удаляет файл из IndexedDB
   */
  static async deleteFile(fileId: string): Promise<boolean> {
    try {
      const db = await this.initDB();
      return new Promise((resolve) => {
        const transaction = db.transaction([this.STORE_NAME], 'readwrite');
        const store = transaction.objectStore(this.STORE_NAME);
        const request = store.delete(fileId);

        request.onsuccess = () => {
          console.log('✅ Файл успешно удален из IndexedDB:', fileId);
          resolve(true);
        };

        request.onerror = () => {
          console.error('❌ Ошибка удаления файла из IndexedDB:', request.error);
          resolve(false);
        };
      });
    } catch (error) {
      console.error('Error deleting file from IndexedDB:', error);
      return false;
    }
  }

  private static generateFileName(originalName: string): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const extension = originalName.includes('.')
      ? originalName.substring(originalName.lastIndexOf('.'))
      : '.audio';

    const nameWithoutExt = originalName.includes('.')
      ? originalName.substring(0, originalName.lastIndexOf('.'))
      : originalName;

    return `${nameWithoutExt}_${timestamp}${extension}`;
  }

  static isFileSystemAPISupported(): boolean {
    return 'indexedDB' in window;
  }
}
