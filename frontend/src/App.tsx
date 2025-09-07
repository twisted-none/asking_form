import React, { useState } from 'react';
import { MessageSquare, Edit3, Send, CheckCircle, AlertCircle } from 'lucide-react';

interface FormData {
  question1: string;
  answer1: string;
  question2: string;
  answer2: string;
  question3: string;
  answer3: string;
}

interface FormErrors {
  [key: string]: string;
}

interface ApiResponse {
  status: string;
  message: string;
  telegram_status?: {
    message_sent: boolean;
    excel_sent: boolean;
  };
  data?: FormData;
}

const InputField = ({ 
  icon: Icon, 
  label, 
  field, 
  type = 'text', 
  placeholder,
  maxLength,
  value,
  error,
  onChange,
  onBlur
}: {
  icon: React.ComponentType<any>;
  label: string;
  field: string;
  type?: string;
  placeholder: string;
  maxLength?: number;
  value: string;
  error?: string;
  onChange: (field: string, value: string) => void;
  onBlur: (field: string) => void;
}) => (
  <div className="space-y-2">
    <label className="block text-purple-200 text-sm font-medium">
      {label}
    </label>
    <div className="relative">
      <Icon className="absolute left-3 top-3 text-purple-400 w-5 h-5 z-10" />
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(field, e.target.value)}
        onBlur={() => onBlur(field)}
        placeholder={placeholder}
        maxLength={maxLength}
        className={`w-full pl-12 pr-4 py-3 bg-gray-900 border-2 rounded-lg text-white placeholder-gray-500 
          transition-all duration-300 focus:outline-none focus:border-purple-500 focus:shadow-purple-glow
          ${error ? 'border-red-500 focus:border-red-500 focus:shadow-red-glow' : 'border-gray-700 hover:border-purple-600'}
        `}
      />
    </div>
    {error && (
      <div className="flex items-center mt-1 text-red-400 text-sm">
        <AlertCircle className="w-4 h-4 mr-1" />
        {error}
      </div>
    )}
  </div>
);

function App() {
  const [formData, setFormData] = useState<FormData>({
    question1: '',
    answer1: '',
    question2: '',
    answer2: '',
    question3: '',
    answer3: ''
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [submitMessage, setSubmitMessage] = useState('');

  // Валидация полей
  const validateField = (field: string, value: string): string => {
    if (!value.trim()) return 'Поле обязательно для заполнения';
    if (value.trim().length < 2) return 'Минимум 2 символа';
    return '';
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Убираем ошибку при изменении поля
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleBlur = (field: string) => {
    const error = validateField(field, formData[field as keyof FormData]);
    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  };

  // Функция для отправки данных на API
  const submitToAPI = async (data: FormData): Promise<ApiResponse> => {
    // Определяем URL API в зависимости от окружения
    const API_BASE_URL = window.location.hostname === 'localhost' 
      ? 'http://localhost:8000' 
      : '/api';

    console.log('🔄 Отправляем данные на:', `${API_BASE_URL}/submit-questions`);
    console.log('📝 Данные формы:', data);

    const response = await fetch(`${API_BASE_URL}/submit-questions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('📡 Статус ответа:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Ошибка API:', errorText);
      throw new Error(`Ошибка сервера: ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ Ответ API:', result);
    return result;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Валидация всех полей
    const newErrors: FormErrors = {};
    Object.keys(formData).forEach(field => {
      const error = validateField(field, formData[field as keyof FormData]);
      if (error) newErrors[field] = error;
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      // Реальная отправка данных на API
      const result = await submitToAPI(formData);
      
      if (result.status === 'success') {
        setSubmitStatus('success');
        let message = result.message;
        
        // Добавляем информацию о статусе Telegram
        if (result.telegram_status) {
          const { message_sent, excel_sent } = result.telegram_status;
          if (message_sent && excel_sent) {
            message += ' Данные отправлены в Telegram!';
          } else if (message_sent) {
            message += ' Сообщение отправлено в Telegram (Excel файл не отправлен)';
          } else {
            message += ' (Ошибка отправки в Telegram)';
          }
        }
        
        setSubmitMessage(message);
        
        // Очищаем форму после успешной отправки
        setTimeout(() => {
          setFormData({
            question1: '',
            answer1: '',
            question2: '',
            answer2: '',
            question3: '',
            answer3: ''
          });
          setSubmitStatus('idle');
        }, 5000);
      } else {
        throw new Error(result.message || 'Неизвестная ошибка');
      }
    } catch (error: any) {
      console.error('❌ Ошибка при отправке формы:', error);
      setSubmitStatus('error');
      setSubmitMessage(error.message || 'Ошибка при отправке формы. Попробуйте еще раз.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Форма вопросов
          </h1>
          <div className="w-32 h-1 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full shadow-purple-glow"></div>
          <p className="text-purple-200 mt-4">Введите вопросы и ответы</p>
        </div>

        <div className="bg-gray-950 p-8 rounded-2xl border border-gray-800 shadow-2xl backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            <InputField
              icon={MessageSquare}
              label="Первый вопрос"
              field="question1"
              placeholder="Введите первый вопрос"
              maxLength={200}
              value={formData.question1}
              error={errors.question1}
              onChange={handleInputChange}
              onBlur={handleBlur}
            />

            <InputField
              icon={Edit3}
              label="Ответ на первый вопрос"
              field="answer1"
              placeholder="Введите ответ"
              maxLength={500}
              value={formData.answer1}
              error={errors.answer1}
              onChange={handleInputChange}
              onBlur={handleBlur}
            />

            <InputField
              icon={MessageSquare}
              label="Второй вопрос"
              field="question2"
              placeholder="Введите второй вопрос"
              maxLength={200}
              value={formData.question2}
              error={errors.question2}
              onChange={handleInputChange}
              onBlur={handleBlur}
            />

            <InputField
              icon={Edit3}
              label="Ответ на второй вопрос"
              field="answer2"
              placeholder="Введите ответ"
              maxLength={500}
              value={formData.answer2}
              error={errors.answer2}
              onChange={handleInputChange}
              onBlur={handleBlur}
            />

            <InputField
              icon={MessageSquare}
              label="Третий вопрос"
              field="question3"
              placeholder="Введите третий вопрос"
              maxLength={200}
              value={formData.question3}
              error={errors.question3}
              onChange={handleInputChange}
              onBlur={handleBlur}
            />

            <InputField
              icon={Edit3}
              label="Ответ на третий вопрос"
              field="answer3"
              placeholder="Введите ответ"
              maxLength={500}
              value={formData.answer3}
              error={errors.answer3}
              onChange={handleInputChange}
              onBlur={handleBlur}
            />

            {submitStatus !== 'idle' && (
              <div className={`flex items-center p-4 rounded-lg ${
                submitStatus === 'success' 
                  ? 'bg-green-900/50 border border-green-500 text-green-300' 
                  : 'bg-red-900/50 border border-red-500 text-red-300'
              }`}>
                {submitStatus === 'success' ? (
                  <CheckCircle className="w-5 h-5 mr-2" />
                ) : (
                  <AlertCircle className="w-5 h-5 mr-2" />
                )}
                {submitMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-all duration-300
                ${isSubmitting 
                  ? 'bg-gray-700 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 transform hover:scale-105 shadow-purple-glow hover:shadow-purple-glow-lg'
                }
              `}
            >
              <div className="flex items-center justify-center">
                <Send className={`w-5 h-5 mr-2 ${isSubmitting ? 'animate-pulse' : ''}`} />
                {isSubmitting ? 'Отправляется...' : 'Отправить форму'}
              </div>
            </button>
          </form>
        </div>

        <div className="text-center mt-6 text-gray-500 text-sm">
          <p>Все поля обязательны для заполнения</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.5); }
          50% { box-shadow: 0 0 30px rgba(168, 85, 247, 0.8); }
        }
        
        .shadow-purple-glow {
          box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
        }
        
        .shadow-purple-glow-lg {
          box-shadow: 0 0 30px rgba(168, 85, 247, 0.5);
        }
        
        .shadow-red-glow {
          box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
        }
        
        .focus\\:shadow-purple-glow:focus {
          box-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
        }
        
        .focus\\:shadow-red-glow:focus {
          box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
        }
      `}</style>
    </div>
  );
}

export default App;