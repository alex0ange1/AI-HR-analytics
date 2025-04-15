import apiClient from './api';

// Логин (получение токена) - отправляется username и password
export const login = async (form) => {
  try {
    const formData = new FormData();
    formData.append('username', form.email); // или form.username — зависит от твоей логики
    formData.append('password', form.password);
    
    const response = await apiClient.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    });
    return response.data; // возвращаем токен
  } catch (error) {
    console.error("Ошибка при авторизации:", error);
    throw error;
  }
};

// Регистрация - отправляется email и password
export const register = async (form) => {
  try {
    const formData = new FormData();
    formData.append('email', form.email); // или form.username — зависит от твоей логики
    formData.append('password', form.password);
    
    const response = await apiClient.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    });
    return response.data; // возвращаем данные о пользователе
  } catch (error) {
    console.error("Ошибка при регистрации:", error);
    throw error;
  }
};


export const logout = () => {
  localStorage.removeItem('token');
};