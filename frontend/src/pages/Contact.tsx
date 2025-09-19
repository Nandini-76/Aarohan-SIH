import React from "react";
import { motion } from "framer-motion";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import SiteHeader from "../components/SiteHeader";

const bgStyle: React.CSSProperties = {
  background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
               radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
               linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
};

const Contact: React.FC = () => {
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
          className="mb-8 md:mb-10"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <motion.h1 
            className="text-4xl md:text-5xl font-extrabold leading-tight [text-shadow:_0_3px_0_rgba(0,0,0,.25)]"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Contact Us
          </motion.h1>
          <motion.p 
            className="mt-3 text-white/90 max-w-3xl"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            Have questions or feedback? Send us a message and we will get back to you.
          </motion.p>
        </motion.header>

        <section className="grid md:grid-cols-2 gap-6 md:gap-8 items-start">
          <motion.div 
            className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
            style={{
              background: "linear-gradient(160deg, rgba(99,102,241,0.95) 0%, rgba(59,130,246,0.95) 100%)",
            }}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <form className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="name" className="text-white">Name</Label>
                  <Input id="name" placeholder="Your name" className="bg-white/80 text-slate-900 placeholder:text-slate-500" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="email" className="text-white">Email</Label>
                  <Input id="email" type="email" placeholder="your.email@example.com" className="bg-white/80 text-slate-900 placeholder:text-slate-500" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="message" className="text-white">Message</Label>
                  <textarea 
                    id="message" 
                    placeholder="Your message..." 
                    rows={5}
                    className="bg-white/80 text-slate-900 placeholder:text-slate-500 px-3 py-2 rounded-md border border-input focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  />
                </div>
                <Button type="submit" className="bg-white text-blue-600 hover:bg-white/90 font-semibold">
                  Send Message
                </Button>
              </form>
            </div>
          </motion.div>

          <motion.div 
            className="rounded-2xl p-6 md:p-8 shadow-[0_15px_35px_-10px_rgba(2,6,23,.45)] ring-1 ring-white/10"
            style={{
              background: "linear-gradient(160deg, rgba(99,102,241,0.95) 0%, rgba(59,130,246,0.95) 100%)",
            }}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="bg-white/10 rounded-xl p-5 md:p-6">
              <h3 className="text-xl font-semibold mb-4">Get in Touch</h3>
              <p className="text-white/80 mb-4">
                AAROHAN is dedicated to improving student success through AI-powered insights.
                Connect with our team for support, partnerships, or feedback.
              </p>
              <div className="space-y-3">
                <p className="text-sm text-white/70">
                  <strong>Project:</strong> Smart India Hackathon 2024
                </p>
                <p className="text-sm text-white/70">
                  <strong>Institution:</strong> Government of Rajasthan
                </p>
                <p className="text-sm text-white/70">
                  <strong>Focus:</strong> AI-Based Dropout Prediction & Counseling
                </p>
              </div>
            </div>
          </motion.div>
        </section>
      </main>
    </motion.div>
  );
};

export default Contact;
