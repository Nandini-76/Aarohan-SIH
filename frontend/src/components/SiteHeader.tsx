import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserRound } from 'lucide-react';

const SiteHeader: React.FC = () => {
  const navigate = useNavigate();

  const goSim = () => {
    navigate('/simulation');
  };
  const goDash = () => {
    navigate('/dashboard');
  };

  return (
    <header className="container mx-auto px-4 md:px-8 py-4 md:py-6 flex items-center justify-between text-white">
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <img 
            src="/assets/logo.svg" 
            alt="AAROHAN Logo" 
            className="w-8 h-8"
          />
          <span className="text-white font-bold text-xl tracking-wide">AAROHAN</span>
          <span className="text-sky-100/70 font-medium text-sm">| 25102</span>
        </Link>
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
      </nav>
      <div className="w-9 h-9 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
        <UserRound className="w-5 h-5 text-sky-700" />
      </div>
    </header>
  );
};

export default SiteHeader;
