import { useNavigate } from 'react-router-dom';
import { logout } from '../utilits/auth';
import FileUpload from '../components/FileUpload'
import { Box, Button } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';

const Analyse = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <FileUpload />
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleLogout}
          endIcon={<LogoutIcon />}
          sx={{ 
            borderRadius: '4px',
            px: 3,
            py: 1,
            bgcolor: '#0078C8',
            '&:hover': {
              bgcolor: '#00396F',
            }
          }}
        >
          Выйти из аккаунта
        </Button>
      </Box>
    </div>
  );
};

export default Analyse;
