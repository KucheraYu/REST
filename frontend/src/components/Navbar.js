import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/users">Users</Link>
      <Link to="/posts">Posts</Link>
      <span style={{ color: '#888', fontSize: 13 }}>{user?.email}</span>
      <button onClick={logout}>Logout</button>
    </nav>
  );
}
