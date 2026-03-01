
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/atoms/Button";
import Text from "../components/atoms/Text";
import Heading from "../components/atoms/Heading";
import Icon from "../components/atoms/Icon";
import Header from "../components/organisms/Header";
import Spinner from "../components/atoms/Spinner";

interface SavedFile {
  id: string;
  fileName: string;
  folderName: string;
  originalName: string;
  timestamp: string;
  size: number;
  type: string;
}

const FilesPage = () => {
  const [files, setFiles] = useState<SavedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      // TODO: Implement file loading
      // const savedFiles = await FileService.getFiles();
      // setFiles(savedFiles);
    } catch (error) {
      console.error('Error loading files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (fileId: string, fileName: string) => {
    try {
      // TODO: Implement file download
      console.log('Downloading file:', fileId, fileName);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const handleDelete = async (fileId: string) => {
    try {
      // TODO: Implement file deletion
      // await FileService.deleteFile(fileId);
      setFiles(files.filter(f => f.id !== fileId));
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Б';
    const k = 1024;
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen">
        <Header />
        <div className="flex items-center justify-center min-h-screen pt-16">
          <div className="text-center">
            <Spinner size="lg" className="mx-auto mb-4" />
            <Text className="text-[var(--color-text-secondary)]">Загрузка файлов...</Text>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen">
      <Header />
      
      <div className="p-6 pt-24">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <Heading level={1} className="text-3xl font-bold mb-2">
                Сохраненные файлы
              </Heading>
              <Text className="text-[var(--color-text-secondary)]">
                Все загруженные аудиофайлы хранятся локально в вашем браузере
              </Text>
            </div>
            
            <Button
              onClick={() => navigate('/upload')}
              variant="primary"
              className="flex items-center gap-2"
            >
              <Icon name="Upload" className="w-4 h-4" />
              Загрузить
            </Button>
          </div>

          {files.length === 0 ? (
            <div className="text-center py-16 bg-[var(--color-bg-secondary)] rounded-lg border border-[var(--color-border)]">
              <Icon name="FileX" className="w-20 h-20 text-[var(--color-text-secondary)]/50 mx-auto mb-4" />
              <Heading level={3} className="text-xl font-semibold mb-2">
                Пока нет сохраненных файлов
              </Heading>
              <Text className="text-[var(--color-text-secondary)] mb-6">
                Загрузите аудиофайл, чтобы увидеть его здесь
              </Text>
              <Button
                onClick={() => navigate('/upload')}
                variant="primary"
                className="inline-flex items-center gap-2"
              >
                <Icon name="Upload" className="w-4 h-4" />
                Загрузить первый файл
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="bg-[var(--color-bg-secondary)] rounded-lg p-6 border border-[var(--color-border)] hover:border-[var(--color-text-purple)] transition-all duration-300 hover:shadow-lg"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-[var(--color-text-purple)]/10 rounded-lg">
                          <Icon name="FileAudio" className="w-5 h-5 text-[var(--color-text-purple)]" />
                        </div>
                        <div>
                          <Text className="font-semibold text-lg text-[var(--color-text-primary)]">
                            {file.originalName}
                          </Text>
                          <Text size="sm" className="text-[var(--color-text-secondary)]">
                            {formatDate(file.timestamp)}
                          </Text>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <Text size="sm" className="text-[var(--color-text-secondary)] uppercase tracking-wider text-xs">
                            Размер
                          </Text>
                          <Text className="font-medium text-[var(--color-text-primary)]">
                            {formatFileSize(file.size)}
                          </Text>
                        </div>
                        <div>
                          <Text size="sm" className="text-[var(--color-text-secondary)] uppercase tracking-wider text-xs">
                            Тип
                          </Text>
                          <Text className="font-medium text-[var(--color-text-primary)]">
                            {file.type?.split('/')[1]?.toUpperCase() || 'Неизвестен'}
                          </Text>
                        </div>
                        <div>
                          <Text size="sm" className="text-[var(--color-text-secondary)] uppercase tracking-wider text-xs">
                            Папка
                          </Text>
                          <Text className="font-medium text-[var(--color-text-primary)]">
                            {file.folderName}
                          </Text>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 lg:flex-col">
                      <Button
                        onClick={() => handleDownload(file.id, file.fileName)}
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-2 justify-center"
                      >
                        <Icon name="Download" className="w-4 h-4" />
                        Скачать
                      </Button>
                      <Button
                        onClick={() => handleDelete(file.id)}
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-2 justify-center border-[var(--color-warning)] text-[var(--color-warning)] hover:bg-[var(--color-warning)] hover:text-white"
                      >
                        <Icon name="Trash2" className="w-4 h-4" />
                        Удалить
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilesPage;