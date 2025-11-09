import { useEffect, useState } from "react";
import Button from "../components/atoms/Button";
import Text from "../components/atoms/Text";
import Heading from "../components/atoms/Heading";
import Icon from "../components/atoms/Icon";
import Header from "../components/organisms/Header";

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
  const [files] = useState<SavedFile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      // const savedFiles = await FileSystemManager.getAllFiles();
      // setFiles(savedFiles);
    } catch (error) {
      console.error('Error loading files:', error);
    } finally {
      setLoading(false);
    }
  };

  // const handleDownload = async (fileId: string, fileName: string) => {
  //   try {
  //     //const file = await FileSystemManager.getFile(fileId);
  //     // if (file) {
  //     //   const url = URL.createObjectURL(file);
  //     //   const a = document.createElement('a');
  //     //   a.href = url;
  //     //   a.download = fileName;
  //     //   a.style.display = 'none';
  //     //   document.body.appendChild(a);
  //     //   a.click();
  //     //   document.body.removeChild(a);
  //     //   setTimeout(() => URL.revokeObjectURL(url), 1000);
  //     // }
  //   } catch (error) {
  //     console.error('Error downloading file:', error);
  //     alert('Ошибка при скачивании файла');
  //   }
  // };

  // const handleDelete = async (fileId: string) => {
  //     try {
  //       //const success = await FileSystemManager.deleteFile(fileId);
  //       // if (success) {
  //       //   setFiles(files.filter(f => f.id !== fileId));
  //       //   alert('Файл успешно удален');
  //       // } else {
  //       //   alert('Ошибка при удалении файла');
  //       // }
  //     } catch (error) {
  //       console.error('Error deleting file:', error);
  //       alert('Ошибка при удалении файла');
  //     }
  // };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  if (loading) {
    return (
      <div className="bg-[#0B0C1C] text-white min-h-screen">
        <Header />
        <div className="flex items-center justify-center min-h-screen pt-16">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
            <p className="text-gray-400">Загрузка файлов...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#0B0C1C] text-white min-h-screen">
      <Header />
      
      <div className="p-6 pt-24"> {/* Добавил pt-24 для отступа под фиксированный хедер */}
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <Heading level={1} className="text-3xl font-bold mb-2">
              Сохраненные файлы
            </Heading>
            <Text className="text-gray-400">
              Все загруженные аудио файлы хранятся локально в вашем браузере
            </Text>
          </div>

          {files.length === 0 ? (
            <div className="text-center py-12">
              <Icon name="FileX" className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <Text className="text-gray-400 text-lg">
                Пока нет сохраненных файлов
              </Text>
              <Text className="text-gray-500 mt-2">
                Загрузите аудио файл, чтобы увидеть его здесь
              </Text>
            </div>
          ) : (
            <div className="grid gap-4">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="bg-[#16182D] rounded-lg p-6 border border-gray-700 hover:border-purple-400 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Icon name="FileAudio" className="w-6 h-6 text-purple-400" />
                        <Text className="font-semibold text-lg truncate">
                          {file.originalName}
                        </Text>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-400">
                        <div>
                          <Text className="text-xs uppercase tracking-wide">Размер</Text>
                          <Text>{formatFileSize(file.size)}</Text>
                        </div>
                        <div>
                          <Text className="text-xs uppercase tracking-wide">Тип</Text>
                          <Text>{file.type || 'Неизвестен'}</Text>
                        </div>
                        <div>
                          <Text className="text-xs uppercase tracking-wide">Папка</Text>
                          <Text>{file.folderName}</Text>
                        </div>
                        <div>
                          <Text className="text-xs uppercase tracking-wide">Дата</Text>
                          <Text>{formatDate(file.timestamp)}</Text>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <Button
                        // onClick={() => handleDownload(file.id, file.fileName)}
                        variant="secondary"
                        className="flex items-center gap-2"
                      >
                        <Icon name="Download" className="w-4 h-4" />
                        Скачать
                      </Button>
                      <Button
                        // onClick={() => handleDelete(file.id)}
                        variant="secondary"
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-red-600"
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