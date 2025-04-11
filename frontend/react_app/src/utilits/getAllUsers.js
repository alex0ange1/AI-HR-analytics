import apiClient from "./api";

export const getUsers = async () => {
    try {
        const response = await apiClient.get('/all_users');
        return response.data;
    } catch (error) {
        console.error("Ошибка при получении данных о пользователях:", error);
        throw error;
    }
};