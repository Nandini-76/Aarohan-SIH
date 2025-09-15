import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { UserRound } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// NOTE: Replace placeholder images and text styles with exact Figma assets and classes.
const Landing: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleSimulate = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/simulation' } });
    } else {
      navigate('/simulation');
    }
  };

  const handleDashboard = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/dashboard' } });
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="relative min-h-screen text-white overflow-hidden" style={{
      background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                   radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                   linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`
    }}>
      {/* Top header */}
      <header className="container mx-auto px-4 md:px-8 py-4 md:py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sky-100/90 font-semibold tracking-widest">25102</span>
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

      {/* Hero */}
      <main className="container mx-auto px-4 md:px-8">
        <section className="grid md:grid-cols-2 gap-10 items-center py-6 md:py-10 lg:py-14">
          <div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight [text-shadow:_0_3px_0_rgba(0,0,0,.25)]">
              <span className="block">Predict. Prevent. Protect</span>
              <span className="block">Student's Futures</span>
            </h1>
            <p className="mt-3 md:mt-4 text-base md:text-lg italic text-white/85">Behind every dropout is a story untold</p>

            <div className="mt-8">
              <Button
                onClick={handleSimulate}
                size="lg"
                className="uppercase tracking-widest text-white font-extrabold px-10 h-12 rounded-full shadow-[0_10px_25px_rgba(0,0,0,.25)]"
                style={{ background: "linear-gradient(90deg, #3b82f6 0%, #a855f7 55%, #ec4899 100%)" }}
              >
                Simulate
              </Button>
            </div>
          </div>

          <div className="flex justify-center">
            <div className="w-64 h-64 md:w-72 md:h-72 lg:w-80 lg:h-80 rounded-full bg-white flex items-center justify-center shadow-[0_25px_60px_-20px_rgba(0,0,0,.35)] overflow-hidden">
              <img
                src="/assets/hero-section.jpeg"
                alt="Graduate working on laptop"
                className="w-full h-full object-cover"
                loading="eager"
              />
            </div>
          </div>
        </section>

        {/* Features row */}
        <section className="pb-16">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {[
              {title: 'Early Risk Detection', desc: 'Identify at-risk students quickly'},
              {title: 'Real-Time Monitoring Track', desc: 'attendance, performance & engagement Live'},
              {title: 'Faculty-Friendly Tools', desc: 'Simple dashboards & reports for teachers'},
              {title: 'Parent Engagement', desc: 'Notify and involve parents proactively'},
              {title: 'Bias-Free Insights', desc: 'Fair predictions across diverse student groups'},
            ].map((card, i) => (
              <div key={i} className="rounded-2xl p-5 shadow-[0_15px_25px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
                   style={{
                     background: 'linear-gradient(160deg, rgba(99,102,241,0.95) 0%, rgba(59,130,246,0.95) 100%)'
                   }}>
                <div className="bg-white/10 rounded-2xl p-4 h-full">
                  <h3 className="text-lg font-semibold text-white">{card.title}</h3>
                  <p className="text-sm text-white/85 mt-2">{card.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Landing;
