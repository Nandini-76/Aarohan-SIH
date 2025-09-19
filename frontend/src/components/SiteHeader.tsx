import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { UserRound } from 'lucide-react';
import { motion } from 'framer-motion';

const SiteHeader: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const goSim = () => {
    navigate('/simulation');
  };
  const goDash = () => {
    navigate('/dashboard');
  };

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const getNavItemClasses = (path: string) => {
    const baseClasses = "transition-all duration-300 relative group";
    const activeClasses = isActive(path) ? "text-white" : "text-white/90 hover:text-white";
    return `${baseClasses} ${activeClasses}`;
  };

  const getUnderlineClasses = (path: string) => {
    const baseClasses = "absolute -bottom-1 left-0 h-0.5 bg-white transition-all duration-300";
    const activeClasses = isActive(path) ? "w-full" : "w-0 group-hover:w-full";
    return `${baseClasses} ${activeClasses}`;
  };

  return (
    <motion.header 
      className="container mx-auto px-4 md:px-8 py-4 md:py-6 flex items-center justify-between text-white"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-all duration-300 group">
          <div className="relative">
            <img 
              src="/assets/logo.png" 
              alt="AAROHAN Logo" 
              className="w-8 h-8 relative z-10 drop-shadow-lg group-hover:scale-110 transition-transform duration-300"
            />
            <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-sm group-hover:blur-md transition-all duration-300"></div>
          </div>
          <span className="text-white font-bold text-xl tracking-wide">AAROHAN</span>
          <span className="text-sky-100/70 font-medium text-sm">| 25102</span>
        </Link>
      </div>
      <nav className="hidden md:flex items-center gap-6 text-white/90">
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Link to="/" className={getNavItemClasses('/')}>
            Home
            <span className={getUnderlineClasses('/')}></span>
          </Link>
        </motion.div>
        <span className="opacity-40">|</span>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <button onClick={goSim} className={getNavItemClasses('/simulation')}>
            Simulation
            <span className={getUnderlineClasses('/simulation')}></span>
          </button>
        </motion.div>
        <span className="opacity-40">|</span>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <button onClick={goDash} className={getNavItemClasses('/dashboard')}>
            Student Dashboard
            <span className={getUnderlineClasses('/dashboard')}></span>
          </button>
        </motion.div>
        <span className="opacity-40">|</span>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Link to="/about" className={getNavItemClasses('/about')}>
            About Us
            <span className={getUnderlineClasses('/about')}></span>
          </Link>
        </motion.div>
        <span className="opacity-40">|</span>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Link to="/contact" className={getNavItemClasses('/contact')}>
            Contact Us
            <span className={getUnderlineClasses('/contact')}></span>
          </Link>
        </motion.div>
      </nav>
      <motion.div 
        className="w-9 h-9 rounded-full bg-white/90 flex items-center justify-center shadow-lg hover:shadow-xl hover:bg-white transition-all duration-300"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <UserRound className="w-5 h-5 text-sky-700" />
      </motion.div>
    </motion.header>
  );
};

export default SiteHeader;
