import apiClient from './api';

export const upload_files = async (files, professionId) => {
    try {
      const formData = new FormData();
  
      // Если пришёл один файл — делаем его массивом
      const filesArray = Array.isArray(files) ? files : [files];
  
      filesArray.forEach(file => {
        formData.append('files', file); // ключ 'files' — должен соответствовать тому, как сервер ожидает
      });
  
      const response = await apiClient.put(`/analyze_files/${professionId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
  
      return response.data;
    } catch (error) {
      console.error("Ошибка при загрузке файлов резюме:", error);
      throw error;
    }
  };
  

export const get_resumes = async (ids) => {
    try {
      const response = await apiClient.post('/get-resumes-by-ids', ids);
      return response.data;
    } catch (error) {
      console.error("Ошибка при получении информации резюме:", error);
      throw error;
    }
  };