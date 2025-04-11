import api from "./api";

// Конфигурация (лучше вынести в .env файл)
const HARDCODED_CREDENTIALS = {
  username: 'd@mail.ru',
  password: 'd'
};

// Таймаут для повторных попыток (мс)
const RETRY_DELAY = 3000;
const MAX_RETRIES = 2;

let authToken = null;
let isAuthenticating = false;

export default {
  async authenticate(retryCount = 0) {
    if (isAuthenticating) return false;
    isAuthenticating = true;

    try {
      const response = await api.post('/token', HARDCODED_CREDENTIALS, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded' // Или 'application/json'
        }
      });

      authToken = response.data.access_token || response.data.token;
      api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
      isAuthenticating = false;
      return true;

    } catch (error) {
      isAuthenticating = false;
      
      // Обработка 422 ошибки
      if (error.response?.status === 422) {
        console.error('Validation errors:', error.response.data);
        return false;
      }

      // Повторная попытка при сетевых ошибках
      if (retryCount < MAX_RETRIES) {
        console.warn(`Retrying auth (${retryCount + 1}/${MAX_RETRIES})...`);
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return this.authenticate(retryCount + 1);
      }

      console.error('Auth failed:', error.message);
      return false;
    }
  },

  getToken() {
    return authToken;
  },

  isAuthenticated() {
    return !!authToken;
  },

  // Для сброса авторизации
  resetAuth() {
    authToken = null;
    delete api.defaults.headers.common['Authorization'];
  }
};




// import api from "./api";


// // config.js (лучше вынести в отдельный файл)
// const HARDCODED_CREDENTIALS = {
//     username: 'd@mail.ru',
//     password: 'd'
//   };
  
//   // auth.js
// //   import axios from 'axios';
// //   import { HARDCODED_CREDENTIALS } from './config';
  
// //   const api = axios.create({
// //     baseURL: 'http://your-backend-api.com'
// //   });
  
//   let authToken = null;
  
//   export default {
//     async authenticate() {
//       try {
//         const response = await api.post('/token', HARDCODED_CREDENTIALS);
//         authToken = response.data.token;
//         api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
//         return true;
//       } catch (error) {
//         console.error('Auto-login failed:', error);
//         return false;
//       }
//     },
  
//     getToken() {
//       return authToken;
//     },
  
//     isAuthenticated() {
//       return !!authToken;
//     }
//   };