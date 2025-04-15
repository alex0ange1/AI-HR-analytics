import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register } from '../utilits/auth'  // импортируем login и register функции
import styles from './Authorization.module.css';

const Authorization = () => {
    const [mode, setMode] = useState('login') // 'login' | 'register'
    const [form, setForm] = useState({ email: '', password: '' })
    const navigate = useNavigate()

    const toggleMode = () => {
        setMode(mode === 'login' ? 'register' : 'login')
    }

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        try {
            if (mode === 'login') {
                const data = await login(form) // использует функцию из твоего api.js
                localStorage.setItem('token', data.access_token)
                navigate('/')
            } else {
                await register(form) // использует функцию регистрации
                alert('Регистрация прошла успешно! Теперь войдите.')
                setMode('login')
            }
        } catch (error) {
            alert('Ошибка: ' + (error?.response?.data?.detail || error.message))
        }
    }

    return (
        <div className={styles.wrapper}>
            <h2>{mode === 'login' ? 'Вход' : 'Регистрация'}</h2>
            <form onSubmit={handleSubmit}>
                <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="Email"
                    required
                />
                <input
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Пароль"
                    required
                />
                <button type="submit">{mode === 'login' ? 'Войти' : 'Зарегистрироваться'}</button>
            </form>
            <p className={styles.text_not_acc}>
                {mode === 'login' ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}{' '}
                <button className={styles.btn_not_acc} type="button" onClick={toggleMode}>
                    {mode === 'login' ? 'Зарегистрироваться' : 'Войти'}
                </button>
            </p>
        </div>
    )
}

export default Authorization