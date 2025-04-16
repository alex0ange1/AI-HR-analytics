import React, { useEffect, useState } from 'react';
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
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import axios from 'axios';

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

  const [professions, setProfessions] = useState([]);
  const [selectedProfessions, setSelectedProfessions] = useState('');
  const [loadingProfessions, setLoadingProfessions] = useState(true);
  const [errorProfessions, setErrorProfessions] = useState(null);

  useEffect(() => {
    const fetchProfessions = async () => {
      try {
        setLoadingProfessions(true);

        const response = await axios.get('/all_professions');
        
        setProfessions(response.data.data);
        setErrorProfessions(null);
      } catch (err) {
        console.error('Ошибка при загрузке профессий:', err);
        setErrorProfessions('Не удалось загрузить список профессий');
      } finally {
        setLoadingProfessions(false);
      }
    };
    fetchProfessions();
  }, []);

  const handleProfessionsChange = (event) => {
    setSelectedProfessions(event.target.value);
    // Сброс результатов предыдущего анализа при смене профессии
    if (report) {
      setReport(null);
    }
  };

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
  
  const handleAnalyze = async () => {
    try {
      // const parse = await parse(); // добавить это, после того как будет api для парсинга резюме 
      
      if (files.length > 0 && selectedProfessions) {
        const analysisReport = {
          summary: `Краткий отчет о сопоставлении резюме с требованиями профессии "${professionName}".`,
          detailed: `Подробный отчет осопоставлении резюме с требованиями профессии "${professionName}".`
        };
        setReport(analysisReport);
      } else {
        if (!files.length) {
          alert('Пожалуйста, выберите файлы для анализа');
        } else if (!selectedProfessions){
          alert('Пожалуйста, выберите профессию для анализа');
        }
      }
    } catch (error) {
      console.error('Ошибка при анализе:', error);
      alert('Произошла ошибка при анализе');
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
          {/* Блок с логотипом */}
          <Box sx={{display: 'flex', justifyContent: 'center', mb: 3}}>
            <img
            src="/logo.png"
            alt="Газпром нефть"
            style={{
              height: '100px',
              objectFit: 'contain'
            }}
            />
          </Box>
          
          
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

          {/* Блок выбора профессии */}
          <Box mb={3}>
            <Typography variant='body1' sx={{ mb: 1}}>
              Выберите профессию для анализа:
            </Typography>

            {loadingProfessions ? (
              <Box display='flex' alignItems='center' gap={2} mt={1}>
                <CircularProgress size={20}/>
                <Typography variant='body2' color='text.secondary'>
                  Загрузка списка профессий...
                </Typography>
              </Box>
            ) : errorProfessions ? (
              <Typography variant='body2' color='error' mt={1}>
                {errorProfessions}
              </Typography>
            ) : (
              <FormControl fullWidth variant='outlined' sx={{ mt: 1 }}>
                <InputLabel> Профессия </InputLabel>
                <Select
                value={selectedProfessions}
                onChange={handleProfessionsChange}
                label="Профессия"
                >
                  <MenuItem value="">
                    <em> Выберите профессию </em>
                  </MenuItem>
                  {Array.isArray(professions) && professions.map((profession) => (
                    <MenuItem key={profession.id} value={profession.id}>
                      {profession.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          </Box>
          
          <Box mb={3}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Загрузите резюме для анализа
            </Typography>
            
            <Box mb={2}>
              <Button
                variant="contained"
                component="label"
                color="primary"
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
            </Box>
            
            {/* Список загруженных файлов */}
            {files.length > 0 && (
              <>
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

              {/* Кнопка анализа появляется только когда есть файлы*/}
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2}}>
                <Button
                variant="contained"
                color="primary"
                onClick={handleAnalyze}
                cx={{
                  px: 3,
                  py: 1
                }}
                >
                  Запустить анализ
                </Button>
              </Box>
              </>
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