import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import SiteHeader from '@/components/SiteHeader';

const bgStyle: React.CSSProperties = {
  background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
               radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
               linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
};

const Contact: React.FC = () => {
  return (
    <div className="min-h-screen text-white" style={bgStyle}>
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12">
        <header className="mb-8 md:mb-10">
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight [text-shadow:_0_3px_0_rgba(0,0,0,.25)]">Contact Us</h1>
          <p className="mt-3 text-white/90 max-w-3xl">
            Have questions or feedback? Send us a message and we’ll get back to you.
          </p>
        </header>

        <section className="grid md:grid-cols-2 gap-6 md:gap-8 items-start">
          <div className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
               style={{
                 background: 'linear-gradient(160deg, rgba(99,102,241,0.95) 0%, rgba(59,130,246,0.95) 100%)',
               }}>
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <form className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="name" className="text-white">Name</Label>
                  <Input id="name" placeholder="Your name" className="bg-white/80 text-slate-900 placeholder:text-slate-500" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="email" className="text-white">Email</Label>
                  <Input id="email" type="email" placeholder="you@example.com" className="bg-white/80 text-slate-900 placeholder:text-slate-500" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="message" className="text-white">Message</Label>
                  <textarea id="message" className="min-h-[140px] rounded-md border-0 bg-white/80 p-3 text-slate-900 placeholder:text-slate-500" placeholder="How can we help?" />
                </div>
                <Button className="w-fit font-semibold" style={{ background: 'linear-gradient(90deg, #3b82f6 0%, #a855f7 55%, #ec4899 100%)' }}>Send Message</Button>
              </form>
            </div>
          </div>

          <div className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
               style={{
                 background: 'linear-gradient(160deg, rgba(59,130,246,0.95) 0%, rgba(168,85,247,0.95) 100%)',
               }}>
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <h2 className="text-2xl font-bold">Reach Us</h2>
              <p className="mt-3 text-white/90">
                We’re building Aarohan as part of the Smart India Hackathon. For collaborations or support, reach out:
              </p>
              <ul className="mt-4 space-y-2 text-white/90">
                <li><span className="font-semibold">Email:</span> support@aarohan.example</li>
                <li><span className="font-semibold">Phone:</span> +91-00000-00000</li>
                <li><span className="font-semibold">Location:</span> Rajasthan, India</li>
              </ul>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Contact;
