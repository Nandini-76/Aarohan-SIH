import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { UserRound, ArrowRight, Shield, Zap, Brain } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

// NOTE: Replace placeholder images and text styles with exact Figma assets and classes.
const Landing: React.FC = () => {
  const navigate = useNavigate();

  const handleSimulate = () => {
    navigate('/simulation');
  };

  const handleDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <motion.div 
      className="relative min-h-screen text-white overflow-hidden" 
      style={{
        background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                     radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                     linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* Top header */}
      <header className="container mx-auto px-4 md:px-8 py-4 md:py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <img 
              src="/assets/logo.png" 
              alt="AAROHAN Logo" 
              className="w-8 h-8 relative z-10 drop-shadow-lg"
            />
            <div className="absolute inset-0 bg-gradient-to-br from-sky-300/30 to-blue-400/30 rounded-full blur-sm"></div>
          </div>
          <span className="text-white font-bold text-xl tracking-wide">AAROHAN</span>
          <span className="text-sky-100/70 font-medium text-sm">| 25102</span>
        </div>
        <nav className="hidden md:flex items-center gap-6 text-white/90">
          <Link to="/" className="hover:text-white">Home</Link>
          <span className="opacity-40">|</span>
          <button onClick={handleSimulate} className="hover:text-white">Simulation</button>
          <span className="opacity-40">|</span>
          <button onClick={handleDashboard} className="hover:text-white">Student Dashboard</button>
          <span className="opacity-40">|</span>
          <Link to="/about" className="hover:text-white">About Us</Link>
          <span className="opacity-40">|</span>
          <Link to="/contact" className="hover:text-white">Contact Us</Link>
        </nav>
        <div className="w-9 h-9 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
          <UserRound className="w-5 h-5 text-sky-700" />
        </div>
      </header>

      {/* Hero */}
      <main className="container mx-auto px-4 md:px-8">
        <section className="grid md:grid-cols-2 gap-10 items-center py-6 md:py-10 lg:py-14">
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <motion.div 
              className="mb-4"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <h2 className="text-2xl md:text-3xl font-bold text-white/90 mb-2">Welcome to</h2>
              <div className="flex items-center gap-3 mb-4">
                <motion.div 
                  className="relative group"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <img 
                    src="/assets/logo.png" 
                    alt="AAROHAN Logo" 
                    className="w-12 h-12 md:w-16 md:h-16 relative z-10 drop-shadow-2xl group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-300/40 via-blue-400/40 to-purple-500/40 rounded-full blur-md group-hover:blur-lg transition-all duration-500"></div>
                  <div className="absolute inset-0 bg-gradient-to-tr from-white/20 to-transparent rounded-full opacity-70"></div>
                </motion.div>
                <motion.h1 
                  className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white"
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.6, delay: 0.7 }}
                >
                  AAROHAN
                </motion.h1>
              </div>
            </motion.div>
            <motion.h3 
              className="text-3xl md:text-4xl lg:text-5xl font-extrabold leading-tight [text-shadow:_0_3px_0_rgba(0,0,0,.25)] mb-4"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.9 }}
            >
              <span className="block text-gradient bg-gradient-to-r from-blue-200 to-purple-200 bg-clip-text text-transparent">Predict. Prevent. Protect</span>
              <span className="block">Student's Futures</span>
            </motion.h3>
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.1 }}
            >
              <p className="mt-3 md:mt-4 text-base md:text-lg italic text-white/85">AI-powered Student Dropout Prevention System</p>
              <p className="text-sm md:text-base text-white/75 mt-2">Behind every dropout is a story untold</p>
            </motion.div>

            <motion.div 
              className="mt-8"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.3 }}
            >
              <motion.button
                onClick={handleSimulate}
                className="group uppercase tracking-widest text-white font-extrabold px-10 h-12 rounded-full shadow-[0_10px_25px_rgba(0,0,0,.25)] hover:shadow-[0_20px_40px_rgba(0,0,0,.35)] transition-all duration-300 inline-flex items-center gap-2"
                style={{ background: "linear-gradient(90deg, #3b82f6 0%, #a855f7 55%, #ec4899 100%)" }}
                whileHover={{ scale: 1.05, boxShadow: "0 20px 40px rgba(0,0,0,0.3)" }}
                whileTap={{ scale: 0.98 }}
              >
                Simulate
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
              </motion.button>
            </motion.div>
          </motion.div>

          <motion.div 
            className="flex justify-center"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            <motion.div 
              className="w-64 h-64 md:w-72 md:h-72 lg:w-80 lg:h-80 rounded-full bg-white flex items-center justify-center shadow-[0_25px_60px_-20px_rgba(0,0,0,.35)] overflow-hidden group hover:shadow-[0_35px_80px_-20px_rgba(0,0,0,.5)] transition-all duration-500"
              whileHover={{ scale: 1.05, rotate: 2 }}
              whileTap={{ scale: 0.98 }}
            >
              <img
                src="/assets/hero-section.jpeg"
                alt="Graduate working on laptop"
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                loading="eager"
              />
            </motion.div>
          </motion.div>
        </section>

        {/* Features row */}
        <motion.section 
          className="pb-16"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.7 }}
        >
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {[
              {title: 'Early Risk Detection', desc: 'Identify at-risk students quickly', icon: Brain},
              {title: 'Real-Time Monitoring', desc: 'Track attendance, performance & engagement', icon: Zap},
              {title: 'Faculty-Friendly Tools', desc: 'Simple dashboards & reports for teachers', icon: Shield},
              {title: 'Parent Engagement', desc: 'Notify and involve parents proactively', icon: Brain},
              {title: 'Bias-Free Insights', desc: 'Fair predictions across diverse student groups', icon: Zap},
            ].map((card, i) => (
              <motion.div 
                key={i} 
                className="rounded-2xl p-5 shadow-[0_15px_25px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10 group hover:shadow-[0_20px_35px_-10px_rgba(2,6,23,.6)] hover:ring-white/20 transition-all duration-500"
                style={{
                  background: 'linear-gradient(160deg, rgba(99,102,241,0.95) 0%, rgba(59,130,246,0.95) 100%)'
                }}
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.9 + (i * 0.1) }}
                whileHover={{ scale: 1.05, y: -5 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="bg-white/10 rounded-2xl p-4 h-full group-hover:bg-white/15 transition-all duration-300">
                  <div className="flex items-center gap-2 mb-2">
                    <card.icon className="w-5 h-5 text-white group-hover:scale-110 transition-transform duration-300" />
                    <h3 className="text-lg font-semibold text-white">{card.title}</h3>
                  </div>
                  <p className="text-sm text-white/85 mt-2 group-hover:text-white/95 transition-colors duration-300">{card.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>
      </main>
    </motion.div>
  );
};

export default Landing;
