import React from 'react';
import SiteHeader from '../components/SiteHeader';

const bgStyle: React.CSSProperties = {
  background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
               radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
               linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
};

const About: React.FC = () => {
  return (
    <div className="min-h-screen text-white" style={bgStyle}>
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12">
        <header className="mb-10 md:mb-12">
          <div className="flex items-center gap-4 mb-6">
            <img 
              src="/assets/logo.svg" 
              alt="AAROHAN Logo" 
              className="w-16 h-16 md:w-20 md:h-20"
            />
            <div>
              <h1 className="text-4xl md:text-5xl font-extrabold leading-tight [text-shadow:_0_3px_0_rgba(0,0,0,.25)]">
                About AAROHAN
              </h1>
              <p className="text-lg md:text-xl text-blue-200 font-medium">AI-Powered Student Success Platform</p>
            </div>
          </div>
          <p className="mt-3 md:mt-4 text-white/90 max-w-3xl text-lg">
            AAROHAN is an advanced AI-based dropout prediction and counseling system, developed as part of the Smart India
            Hackathon for the Government of Rajasthan. Our mission is to identify students at risk of dropping out and
            provide timely support through teachers, parents, and counselors.
          </p>
        </header>

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
    </div>
  );
};

export default About;
