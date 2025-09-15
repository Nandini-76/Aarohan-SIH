import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserRound } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';

const SiteHeader: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const goSim = () => {
    if (!isAuthenticated) navigate('/login', { state: { from: '/simulation' } });
    else navigate('/simulation');
  };
  const goDash = () => {
    if (!isAuthenticated) navigate('/login', { state: { from: '/dashboard' } });
    else navigate('/dashboard');
  };

  return (
    <header className="container mx-auto px-4 md:px-8 py-4 md:py-6 flex items-center justify-between text-white">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-sky-100/90 font-semibold tracking-widest">25102</Link>
      </div>
      <nav className="hidden md:flex items-center gap-6 text-white/90">
        <Link to="/" className="hover:text-white">Home</Link>
        <span className="opacity-40">|</span>
        <button onClick={goSim} className="hover:text-white">Simulation</button>
        <span className="opacity-40">|</span>
        <button onClick={goDash} className="hover:text-white">Student Dashboard</button>
        <span className="opacity-40">|</span>
        <Link to="/about" className="hover:text-white">About Us</Link>
        <span className="opacity-40">|</span>
        <Link to="/contact" className="hover:text-white">Contact Us</Link>
        <span className="opacity-40">|</span>
        {!isAuthenticated ? (
          <>
            <Link to="/login" className="hover:text-white">Sign in</Link>
          </>
        ) : (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-white/90 flex items-center justify-center text-sky-700 font-semibold">
                {(user?.username?.[0] || 'U').toUpperCase()}
              </div>
              <span className="text-white/90">{user?.username}</span>
            </div>
            <button onClick={logout} className="px-3 py-1 rounded-md bg-white/10 hover:bg-white/20">Sign out</button>
          </div>
        )}
      </nav>
      <div className="w-9 h-9 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
        <UserRound className="w-5 h-5 text-sky-700" />
      </div>
    </header>
  );
};

export default SiteHeader;
