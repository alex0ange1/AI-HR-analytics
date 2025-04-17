from datetime import datetime

import io

from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

from yargy import Parser, rule, or_
from yargy.predicates import dictionary, gram, eq, in_, type as yargy_type
from yargy.interpretation import fact
from yargy.tokenizer import MorphTokenizer
import re

from fastapi import HTTPException, status, UploadFile


class Analyzer:
    def __init__(self):
        self.tokenizer = MorphTokenizer()
        self.LEVEL_TERMS = {
            1: [
                "базовый", "начальный", "изучал", "знаком", "основы",
                "начинающий", "новичок", "junior", "стажер", "знакомство",
                "освоил", "изучала", "базовые", "простые", "начал",
                "учебные", "тренировочные", "вводный", "ознакомительный",
                "младший", "ограниченный", "слабые", "нет опыта",
                "базовый уровень", "начальные знания", "пробовал",
                "имею представление", "непродвинутый", "элементарный",
                "перспектива роста", "осваиваю", "в процессе изучения",
                "ограниченный production-опыт", "слабые знания",
                "нет сложных проектов", "младший специалист"
            ],
            2: [
                "средний", "опыт", "разрабатывал", "реализовывал", "применял",
                "реализовал", "использовал", "участвовал", "работал", "middle",
                "применяла", "достиг", "улучшил", "построил", "создал",
                "настройка", "оптимизация", "анализ", "внедрение", "разработка",
                "практический", "реальный", "проектный", "коммерческий",
                "автоматизировал", "участвовал в разработке", "a/b тестирование",
                "опыт работы", "1-3 года", "промежуточный", "развертывание",
                "дашборды", "отчеты", "подготовка данных", "моделирование",
                "аналитик", "реализация", "применение", "внедрение",
                "участвовал в разработке модели", "автоматизировал отчеты",
                "подготовка данных для ML", "a/b тестирование",
                "разведочный анализ данных", "создавал дашборды",
                "моделирование бизнес-процессов", "опыт работы 1-3 года"
            ],
            3: [
                "продвинутый", "эксперт", "архитектура", "оптимизация", "руководство",
                "senior", "lead", "обучение", "менторство", "внедрение",
                "стратегия", "управление", "проектирование", "решение", "автоматизация",
                "масштабирование", "интеграция", "дизайн", "планирование", "координация",
                "production", "промышленная эксплуатация", "mlops", "ci/cd",
                "оптимизация производительности", "руководил проектом", "обучал команду",
                "архитектура решений", "стратегическое планирование", "технический лидер"
            ]
        }

        self.LEVEL_PHRASES = {
            1: [
                "имею представление", "изучал основы", "базовые знания",
                "начальный уровень", "знаком с", "знакома с",
                "имею опыт работы на базовом уровне", "учебные проекты",
                "базовый опыт с", "ограниченный production-опыт",
                "слабые знания", "нет сложных проектов", "младший специалист",
                "перспектива роста", "только начинаю", "осваиваю",
                "в процессе изучения", "пока только основы",
                "базовый уровень sql", "базовый опыт с pytorch/keras",
                "подходит для junior data scientist", "младший ml engineer"
            ],
            2: [
                "коммерческий опыт", "реальные проекты", "практический опыт",
                "успешно реализовал", "достиг точности", "улучшил показатели",
                "средний уровень", "опыт внедрения", "работал над",
                "опыт работы 1-3 года", "участвовал в разработке модели",
                "автоматизировал отчеты", "подготовка данных для ML",
                "a/b тестирование", "разведочный анализ данных",
                "создавал дашборды", "моделирование бизнес-процессов",
                "реализация алгоритмов", "применение ML на практике",
                "работа с промышленными данными", "внедрение решений",
                "участвовал в разработке модели скоринга",
                "auc 0.85", "помогал в подготовке данных для ml-моделей",
                "проводил разведочный анализ данных", "создавал дашборды в tableau"
            ],
            3: [
                "руководил проектом", "оптимизировал производительность",
                "архитектура системы", "обучал коллег", "разработал стратегию",
                "продвинутый уровень", "экспертные знания", "комплексные решения",
                "промышленная эксплуатация моделей", "настройка mlops",
                "интеграция ML в production", "масштабирование решений",
                "техническое руководство", "стратегическое планирование",
                "оптимизация инфраструктуры", "менторство junior-специалистов",
                "архитектура data pipeline", "управление ML-проектами",
                "внедрение best practices", "разработка стратегии AI"
            ]
        }

        self.CompetencyMatch = fact("CompetencyMatch", ["name", "level"])
        self.parser = None

    def _preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[\/()\-—.,;:«»]', ' ', text)
        return text

    def _initialize_parser(self, competencies):
        # Создаем словарь для поиска компетенций по ключевым словам
        comp_dict = {}
        for comp in competencies:
            keywords = re.findall(r'\b\w{4,}\b', comp["name"].lower())  # только слова длиной 4+ символа
            for kw in keywords:
                comp_dict.setdefault(kw, []).append((comp["name"], comp["level"]))

        # Правило для поиска компетенций
        competency_rule = rule(
            or_(*[dictionary([kw for kw in comp_dict.keys()])]).interpretation(self.CompetencyMatch.name)
        )

        # Правила для уровней
        def make_level_rule(terms, level):
            return or_(
                rule(dictionary(terms)).interpretation(self.CompetencyMatch.level.const(level)),
                *[rule(dictionary(phrase.split())).interpretation(self.CompetencyMatch.level.const(level))
                  for phrase in self.LEVEL_PHRASES[level]]
            )

        level_1_rule = make_level_rule(self.LEVEL_TERMS[1], 1)
        level_2_rule = make_level_rule(self.LEVEL_TERMS[2], 2)
        level_3_rule = make_level_rule(self.LEVEL_TERMS[3], 3)

        # Основное правило - ищем сочетания уровня и компетенции в любом порядке
        main_rule = or_(
            rule(level_1_rule, competency_rule),
            rule(level_2_rule, competency_rule),
            rule(level_3_rule, competency_rule),
            rule(competency_rule, level_1_rule),
            rule(competency_rule, level_2_rule),
            rule(competency_rule, level_3_rule),
            # Также учитываем компетенции без явного указания уровня (по умолчанию уровень 1)
            competency_rule.interpretation(self.CompetencyMatch.level.const(1))
        ).interpretation(self.CompetencyMatch)

        self.parser = Parser(main_rule, tokenizer=self.tokenizer)
        return comp_dict

    def analyze(self, text, competencies_data):
        competencies = competencies_data.get("competencies", [])
        comp_dict = self._initialize_parser(competencies)

        processed_text = self._preprocess_text(text)
        matches = self.parser.findall(processed_text)

        # Собираем результаты
        results = {}
        for match in matches:
            if match.fact.name and match.fact.level:
                # Находим все полные названия компетенций, содержащие найденное ключевое слово
                for comp_name, comp_level in comp_dict.get(match.fact.name, []):
                    # Если уровень из текста выше базового уровня компетенции, используем его
                    final_level = match.fact.level
                    if comp_name not in results or final_level > results[comp_name]:
                        results[comp_name] = final_level

        # Форматируем результат в требуемую структуру
        formatted_results = {
            "competencies": [
                {"name": name, "level": level}
                for name, level in sorted(results.items(), key=lambda x: -x[1])
            ]
        }

        return formatted_results

    def extract_contact_info(self, text):
        """
        Извлекает контактную информацию из текста резюме.
        Возвращает словарь с ключами: first_name, last_name, birth_date, city, phone, email.
        Если какой-то параметр не найден, сохраняет None.
        """
        # Инициализация правил для извлечения информации

        # Имя и фамилия
        Name = fact('Name', ['first_name', 'last_name'])
        name_rule = or_(
            rule(
                gram('Surn').interpretation(Name.last_name),
                gram('Name').interpretation(Name.first_name)
            ),
            rule(
                gram('Name').interpretation(Name.first_name),
                gram('Surn').interpretation(Name.last_name)
            )
        ).interpretation(Name)
        name_parser = Parser(name_rule, tokenizer=self.tokenizer)

        # Дата рождения
        Date = fact('Date', ['birth_date'])
        INT = yargy_type('INT')
        date_rule = rule(
            or_(
                rule(INT, eq('.'), INT, eq('.'), INT),  # DD.MM.YYYY
                rule(INT, eq('-'), INT, eq('-'), INT),  # DD-MM-YYYY
                rule(INT, eq('/'), INT, eq('/'), INT)  # DD/MM/YYYY
            ).interpretation(Date.birth_date)
        ).interpretation(Date)
        date_parser = Parser(date_rule)

        # Город
        City = fact('City', ['city'])
        city_rule = rule(
            gram('Geox').interpretation(City.city)
        ).interpretation(City)
        city_parser = Parser(city_rule, tokenizer=self.tokenizer)

        # Извлечение информации
        contact_info = {
            'first_name': None,
            'last_name': None,
            'birth_date': None,
            'city': None,
            'phone': 'None',
            'email': None
        }

        # Имя и фамилия
        for match in name_parser.findall(text):
            if match.fact.first_name and match.fact.last_name:
                contact_info['first_name'] = match.fact.first_name.capitalize()
                contact_info['last_name'] = match.fact.last_name.capitalize()
                break

        # Дата рождения
        for match in date_parser.findall(text):
            if match.fact.birth_date:
                try:
                    date_str = ''.join([t.value for t in match.tokens])
                    for fmt in ('%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%y', '%d-%m-%y', '%d/%m/%y'):
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            contact_info['birth_date'] = dt.strftime('%d.%m.%Y')
                            break
                        except ValueError:
                            continue
                except:
                    continue

        # Город
        for match in city_parser.findall(text):
            if match.fact.city:
                contact_info['city'] = match.fact.city.capitalize()
                break

        # Телефон
        phone_regex = re.compile(r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
        phone_match = phone_regex.search(text)
        if phone_match:
            phone = phone_match.group(0)
            phone = re.sub(r'[^\d]', '', phone)
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            contact_info['phone'] = phone

        # Email
        email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        match = email_regex.search(text)
        if match:
            contact_info['email'] = match.group(0).lower()

        return contact_info

    async def parse_pdf(self, file: UploadFile) -> str:
        """Парсер PDF файлов с использованием pdfminer"""
        try:
            # Читаем содержимое файла в bytes
            contents = await file.read()
            # Используем io.BytesIO для работы с pdfminer
            with io.BytesIO(contents) as pdf_file:
                text = pdf_extract_text(pdf_file)
            return text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF file: {str(e)}"
            )

    async def parse_docx(self, file: UploadFile) -> str:
        """Парсер DOCX файлов с использованием python-docx"""
        try:
            contents = await file.read()
            with io.BytesIO(contents) as docx_file:
                doc = Document(docx_file)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse DOCX file: {str(e)}"
            )

    async def parse_file(self, file: UploadFile) -> str:
        """Универсальный парсер файлов разных форматов"""
        filename = file.filename.lower()

        if filename.endswith('.pdf'):
            return await self.parse_pdf(file)
        elif filename.endswith(('.doc', '.docx')):
            return await self.parse_docx(file)
        elif filename.endswith(('.txt', '.text')):
            return await file.read().decode('utf-8')
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {file.filename}"
            )
