import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';

const SignUp: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Hook into your auth flow or mock for demo
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#0c2f52] flex items-center justify-center p-6">
      <Card className="w-full max-w-4xl bg-[#1f4d73] border-[#2b5d86] shadow-[0_25px_60px_-20px_rgba(0,0,0,.5)]">
        <CardContent className="p-6 md:p-10">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="bg-[#0a2742] rounded-lg overflow-hidden aspect-[3/4] flex items-center justify-center">
              <img src="/assets/signin.jpeg" alt="Sign up poster" className="w-full h-full object-cover" />
            </div>
            <div>
              <h1 className="text-white text-3xl font-bold mb-6">Create your account</h1>
              <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-white/90">Full name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required className="h-11 rounded-full bg-white text-black placeholder:text-black/60" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white/90">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="h-11 rounded-full bg-white text-black placeholder:text-black/60" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-white/90">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="h-11 rounded-full bg-white text-black placeholder:text-black/60" />
            </div>
            <Button type="submit" className="w-full h-11 rounded-md font-semibold text-white" style={{ background: 'linear-gradient(180deg, #5bb7ff 0%, #2563eb 100%)' }}>Sign up</Button>
              </form>
              <p className="text-sm text-white/80 mt-4">
                Already have an account? <Link to="/login" className="underline underline-offset-4">Sign in</Link>
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignUp;
