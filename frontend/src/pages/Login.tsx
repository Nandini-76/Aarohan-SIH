import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent } from '../components/ui/card';
import { useAuth } from '../contexts/AuthContext';
import SiteHeader from '../components/SiteHeader';
import { useToast } from '../hooks/use-toast';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        toast({ title: "Login successful", description: "Welcome to the Student Risk Prediction Dashboard" });
        const redirectTo = (location.state as any)?.from || '/dashboard';
        navigate(redirectTo, { replace: true });
      } else {
        toast({
          title: "Login failed",
          description: "Please check your credentials and try again",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const bgStyle: React.CSSProperties = {
    background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                 radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                 linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
  };

  return (
    <div className="min-h-screen text-white" style={bgStyle}>
      <SiteHeader />
      <div className="container mx-auto px-4 md:px-8 py-8 md:py-12 flex items-center justify-center">
      <Card className="w-full max-w-4xl bg-[#1f4d73] border-[#2b5d86] shadow-[0_25px_60px_-20px_rgba(0,0,0,.5)]">
        <CardContent className="p-6 md:p-10">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="bg-[#0a2742] rounded-lg overflow-hidden aspect-[3/4] flex items-center justify-center">
              <img src="/assets/signin.jpeg" alt="Sign in poster" className="w-full h-full object-cover" />
            </div>

            <div>
              <h1 className="text-white text-3xl md:text-4xl font-bold mb-6">Welcome to Aarohan</h1>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-white/90">Enter Id:</Label>
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    className="h-11 rounded-full bg-white text-black placeholder:text-black/60"
                    placeholder="Enter Id:"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-white/90">Enter Password:</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="h-11 rounded-full bg-white text-black placeholder:text-black/60 pr-10"
                      placeholder="Enter Password:"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 text-black/60 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? (<EyeOff className="h-4 w-4" />) : (<Eye className="h-4 w-4" />)}
                    </Button>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-40 h-11 rounded-md font-semibold text-white"
                  style={{
                    background: 'linear-gradient(180deg, #5bb7ff 0%, #2563eb 100%)'
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? 'Signing in...' : 'Sign In'}
                </Button>
              </form>

              <p className="mt-6 text-white/80 text-sm">
                Having trouble signing in? <button className="italic underline underline-offset-4">forgot password</button>
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  );
};

export default Login;