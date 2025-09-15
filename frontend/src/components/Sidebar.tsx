import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, FlaskConical, User, LogOut, GraduationCap, Shield } from 'lucide-react';
import { cn } from '@/lib/utils.ts';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';

const Sidebar: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ];

  return (
    <div className="h-screen w-64 bg-gradient-hero border-r border-border/20 flex flex-col">
      {/* Logo/Header */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">
              Student Guardian
            </h1>
            <p className="text-xs text-white/70">
              Risk Prediction System
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2 mt-3 px-2 py-1 bg-white/10 rounded-md">
          <Shield className="w-3 h-3 text-white/70" />
          <span className="text-xs text-white/70">Government of Rajasthan</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 group",
                isActive
                  ? "bg-white/20 text-white shadow-glow"
                  : "text-white/70 hover:text-white hover:bg-white/10"
              )
            }
          >
            <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-white/10">
        <Button
          onClick={handleLogout}
          variant="ghost" 
          className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10 group"
        >
          <LogOut className="w-5 h-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
          Logout
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;