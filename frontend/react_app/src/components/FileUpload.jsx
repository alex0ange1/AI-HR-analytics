import React, { useState } from 'react';
import { jsPDF } from 'jspdf';

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [report, setReport] = useState(null);
  const [isDetailed, setIsDetailed] = useState(false);

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const validFiles = selectedFiles.filter(file =>
      file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );

    if (validFiles.length > 0) {
      setFiles(validFiles);
    } else {
      alert('Пожалуйста, выберите файлы форматов PDF или DOCX');
    }
  };

  const handleAnalyze = () => {
    // Эмулируем отправку файлов на сервер и получение отчета
    // Обычно тут будет код для отправки файлов на бэк через fetch или axios
    // Но для этого примера мы просто генерируем фиктивный отчет
    if (files.length > 0) {
      const analysisReport = {
        summary: "Краткий отчет о соответствии компетенций.",
        detailed: "Подробный отчет о соответствии компетенций. Он содержит более глубокий анализ, который описывает каждый аспект в деталях."
      };
      setReport(analysisReport);
    } else {
      alert('Пожалуйста, выберите файлы для анализа');
    }
  };

  const handleDownloadPDF = () => {
    if (report) {
      const doc = new jsPDF();

      const reportText = isDetailed ? report.detailed : report.summary;
      doc.text(reportText, 10, 10);
      doc.save('report.pdf');
    }
  };

  return (
    <div>
      <h1>Анализ соответствия компетенций</h1>
      
      {/* Поле для загрузки файлов */}
      <input
        type="file"
        accept=".pdf,.docx"
        multiple
        onChange={handleFileChange}
      />

      {/* Кнопка для запуска анализа */}
      <button onClick={handleAnalyze}>Запустить анализ</button>

      {/* Отображение отчета после анализа */}
      {report && (
        <div>
          <h3>Отчет:</h3>
          <p>{isDetailed ? report.detailed : report.summary}</p>
          <button onClick={() => setIsDetailed(!isDetailed)}>
            {isDetailed ? 'Сделать отчет кратким' : 'Сделать отчет подробным'}
          </button>
        </div>
      )}

      {/* Кнопка для скачивания отчета в формате PDF */}
      {report && (
        <button onClick={handleDownloadPDF}>
          Скачать отчет в формате PDF
        </button>
      )}
    </div>
  );
};

export default FileUpload;