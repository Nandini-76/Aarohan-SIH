import React from 'react';
import { motion } from 'framer-motion';
import SiteHeader from '../components/SiteHeader';

const bgStyle: React.CSSProperties = {
  background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
               radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
               linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
};

const About: React.FC = () => {
  return (
    <motion.div 
      className="min-h-screen text-white" 
      style={bgStyle}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12">
        <motion.header 
          className="mb-10 md:mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="flex items-center gap-4 mb-6">
            <motion.div 
              className="relative group"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <img 
                src="/assets/logo.png" 
                alt="AAROHAN Logo" 
                className="w-16 h-16 md:w-20 md:h-20 relative z-10 drop-shadow-2xl group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/40 via-blue-500/40 to-purple-600/40 rounded-full blur-lg group-hover:blur-xl transition-all duration-500"></div>
              <div className="absolute inset-0 bg-gradient-to-tr from-white/30 to-transparent rounded-full opacity-60"></div>
            </motion.div>
            <div>
              <motion.h1 
                className="text-4xl md:text-5xl font-extrabold leading-tight [text-shadow:_0_3px_0_rgba(0,0,0,.25)]"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                About AAROHAN
              </motion.h1>
              <motion.p 
                className="text-lg md:text-xl text-blue-200 font-medium"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                AI-Powered Student Success Platform
              </motion.p>
            </div>
          </div>
          <motion.p 
            className="mt-3 md:mt-4 text-white/90 max-w-3xl text-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            AAROHAN is an advanced AI-based dropout prediction and counseling system, developed as part of the Smart India
            Hackathon for the Government of Rajasthan. Our mission is to identify students at risk of dropping out and
            provide timely support through teachers, parents, and counselors.
          </motion.p>
        </motion.header>

        <section className="grid gap-6 md:gap-8">
          {/* About Us Panel */}
          <div className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
               style={{
                 background: 'linear-gradient(160deg, rgba(99,102,241,0.95) 0%, rgba(59,130,246,0.95) 100%)',
               }}>
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <h2 className="text-2xl md:text-3xl font-bold">About AAROHAN</h2>
              <p className="mt-3 text-white/90">
                Using data-driven insights, AAROHAN generates a simple color-coded risk score to track student
                performance, attendance, financial challenges, and other key factors. This helps schools intervene
                early and ensure every child continues their education without unnecessary hurdles.
              </p>
            </div>
          </div>

          {/* Our Vision Panel */}
          <div className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
               style={{
                 background: 'linear-gradient(160deg, rgba(59,130,246,0.95) 0%, rgba(168,85,247,0.95) 100%)',
               }}>
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <h2 className="text-2xl md:text-3xl font-bold">Our Vision</h2>
              <p className="mt-3 text-white/90">
                To create a future where no child is forced to leave education due to avoidable circumstances, by
                empowering institutions with AI-driven tools that bridge the gap between students in need and timely
                support.
              </p>
            </div>
          </div>

          {/* Our Team Panel */}
          <div className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
               style={{
                 background: 'linear-gradient(160deg, rgba(236,72,153,0.95) 0%, rgba(168,85,247,0.95) 100%)',
               }}>
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <h2 className="text-2xl md:text-3xl font-bold">Our Team</h2>
              <p className="mt-3 text-white/90">
                Aarohan is built by a passionate group of B.Tech/B.Sc students, driven by the belief that technology can
                solve real-world problems. Together, we combine our skills in artificial intelligence, data science,
                software development, and user-centric design to contribute towards strengthening the education system
                of our nation.
              </p>
            </div>
          </div>
        </section>
      </main>
    </motion.div>
  );
};

export default About;
