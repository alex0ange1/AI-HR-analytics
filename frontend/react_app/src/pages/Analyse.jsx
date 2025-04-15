import { useNavigate } from 'react-router-dom';
import { logout } from '../utilits/auth';
import FileUpload from '../components/FileUpload'

const Analyse = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      {/* <h1>Главная страница</h1> */}
      <FileUpload></FileUpload>
      <button onClick={handleLogout}>Выйти из аккаунта</button>
    </div>
  );
};

export default Analyse;
