export interface User {
  id: string;
  username: string;
  profile?: string;
  settings?: string;
}

export interface Lecture {
  lecture_id: string;
  user_id: string;
  status: 'pending' | 'transcribing' | 'transcribed' | 'summarizing' | 'done' | 'failed';
  task_id?: string;
}

export interface TranscriptionResult {
  lecture_id: string;
  transcription: string;
}

// Имитируем базу данных пользователей
const mockUsers: User[] = [
  {
    id: 'demo-user-123',
    username: 'demo',
    profile: 'Демо пользователь',
    settings: '{}'
  }
];

// Текущий аутентифицированный пользователь (для демо)
let currentUser: User | null = null;

export const mockApi = {
  // Регистрация нового пользователя
  async register(username: string): Promise<User> {
    console.log('📝 Регистрируем пользователя:', username);
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Проверяем, не существует ли уже пользователь
    const existingUser = mockUsers.find(user => user.username === username);
    if (existingUser) {
      throw new Error('Пользователь с таким именем уже существует');
    }
    
    const newUser: User = {
      id: 'user-' + Date.now(),
      username: username,
      profile: 'Новый пользователь',
      settings: '{}'
    };
    
    mockUsers.push(newUser);
    currentUser = newUser;
    
    return newUser;
  },

  // Аутентификация (вход)
  async login(username: string, password: string): Promise<User> {
    console.log('🔐 Вход пользователя:', username);
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // В демо-режиме всегда успешный вход для демо пользователя
    if (username === 'demo' && password === 'demo') {
      currentUser = mockUsers[0];
      return mockUsers[0];
    }
    
    // Или ищем пользователя по имени
    const user = mockUsers.find(u => u.username === username);
    if (user) {
      currentUser = user;
      return user;
    }
    
    throw new Error('Неверное имя пользователя или пароль');
  },

  // Выход
  async logout(): Promise<void> {
    console.log('🚪 Выход пользователя');
    await new Promise(resolve => setTimeout(resolve, 200));
    currentUser = null;
  },

  // Получение текущего пользователя
  async getCurrentUser(): Promise<User | null> {
    await new Promise(resolve => setTimeout(resolve, 100));
    return currentUser;
  },

  // Загрузка аудио (только для аутентифицированных пользователей)
  async uploadAudio(filePath: string): Promise<Lecture> {
    console.log('🎵 Загружаем аудио:', filePath);
    
    if (!currentUser) {
      throw new Error('Требуется аутентификация');
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      lecture_id: 'lecture-' + Date.now(),
      user_id: currentUser.id,
      status: 'pending',
      task_id: 'task-' + Date.now()
    };
  },

  // Проверка статуса
  async getStatus(lectureId: string): Promise<Lecture> {
    console.log('🔄 Проверяем статус:', lectureId);
    
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const statuses: Array<'pending' | 'transcribing' | 'transcribed'> = [
      'pending', 'transcribing', 'transcribed'
    ];
    
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    
    return {
      lecture_id: lectureId,
      user_id: currentUser?.id || 'unknown',
      status: randomStatus,
      task_id: 'mock-task-123'
    };
  },

  // Получение результата
  async getResult(lectureId: string): Promise<TranscriptionResult> {
    console.log('📄 Получаем результат:', lectureId);
    
    if (!currentUser) {
      throw new Error('Требуется аутентификация');
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockTranscriptions = [
      `# Конспект лекции по искусственному интеллекту\n\n## Основные темы:\n- Машинное обучение и его виды\n- Нейронные сети и глубокое обучение\n- Применение ИИ в реальном мире\n\n## Ключевые идеи:\n1. ИИ меняет подход к решению сложных задач\n2. Важно понимать ограничения технологий\n3. Этические аспекты разработки ИИ`,

      `# Лекция о продуктивности\n\n## Главные принципы:\n- Фокусировка на одной задаче\n- Регулярные перерывы\n- Приоритизация дел\n\n## Советы:\n• Используйте технику Pomodoro\n• Планируйте день с вечера\n• Делегируйте рутинные задачи`
    ];
    
    const randomText = mockTranscriptions[Math.floor(Math.random() * mockTranscriptions.length)];
    
    return {
      lecture_id: lectureId,
      transcription: randomText
    };
  }
};