import React, { useState } from 'react';
import { jsPDF } from 'jspdf';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Container,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const Theme = createTheme({
  palette: {
    primary: {
      main: '#0078C8', // основной синий
    },
    secondary: {
      main: '#00396F', // темно-синий
    },
    background: {
      default: '#F6F8FB',
    },
  },
});


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
      setFiles([...files, ...validFiles]);
    } else {
      alert('Пожалуйста, выберите файлы форматов PDF или DOCX');
    }
    
    // Сбрасываем значение input, чтобы можно было повторно загрузить тот же файл
    event.target.value = '';
  };

  const handleRemoveFile = (index) => {
    const newFiles = [...files];  // Создаем копию массива файлов
    newFiles.splice(index, 1);    // Удаляем элемент с указанным индексом
    setFiles(newFiles);           // Обновляем состояние с новым массивом
    
    // Сброс результатов анализа при удалении файла
    if (report) {
      setReport(null);
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
    <ThemeProvider theme={Theme}>
      <Container maxWidth="md" sx={{ py: 3 }}>
        <Paper elevation={2} sx={{ p: 3, borderRadius: '8px' }}>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 2, 
              color: 'primary.main',
              fontWeight: 'bold' 
            }}
          >
            Анализ соответствия компетенций
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Box mb={3}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Загрузите резюме и должностные инструкции для анализа
            </Typography>
            
            <Box mb={2}>
              <Button
                variant="contained"
                component="label"
                color="primary"
                sx={{ mr: 1 }}
              >
                Выбрать файлы
                <input
                  type="file"
                  hidden
                  accept=".pdf,.docx"
                  multiple
                  onChange={handleFileChange}
                />
              </Button>
              
              <Button
                variant="contained"
                color="primary"
                onClick={handleAnalyze}
                disabled={files.length === 0}
              >
                Запустить анализ
              </Button>
            </Box>
            
            {/* Список загруженных файлов */}
            {files.length > 0 && (
              <Paper variant="outlined" sx={{ p: 1, mb: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Загруженные файлы ({files.length}):
                </Typography>
                <List dense>
                  {files.map((file, index) => (
                    <ListItem
                      key={index}
                      secondaryAction={
                        <IconButton edge="end" onClick={() => handleRemoveFile(index)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      }
                    >
                      <ListItemText 
                        primary={file.name}
                        secondary={file.type.includes('pdf') ? 'PDF' : 'DOCX'} 
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            )}
          </Box>
          
          {/* Отображение отчета после анализа */}
          {report && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: '4px' }}>
              <Typography variant="h6" sx={{ mb: 2, color: 'secondary.main' }}>
                Результаты анализа
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={isDetailed}
                    onChange={() => setIsDetailed(!isDetailed)}
                    color="primary"
                  />
                }
                label={isDetailed ? "Подробный отчет" : "Краткий отчет"}
                sx={{ mb: 1 }}
              />
              
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'white', whiteSpace: 'pre-line' }}>
                <Typography variant="body2">
                  {isDetailed ? report.detailed : report.summary}
                </Typography>
              </Paper>
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleDownloadPDF}
                >
                  Скачать отчет в PDF
                </Button>
              </Box>
            </Box>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
};

export default FileUpload;