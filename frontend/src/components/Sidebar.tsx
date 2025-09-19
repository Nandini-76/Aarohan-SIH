import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, FlaskConical, User, GraduationCap, Shield } from 'lucide-react';
import { cn } from '../lib/utils';

const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ];

  return (
    <div className="h-screen w-64 bg-gradient-hero border-r border-border/20 flex flex-col">
      {/* Logo/Header */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-white/30 to-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center border border-white/20 shadow-lg hover:shadow-xl transition-all duration-300 group relative">
            <img 
              src="/assets/logo.png" 
              alt="AAROHAN Logo" 
              className="w-6 h-6 drop-shadow-md group-hover:scale-110 transition-transform duration-300"
            />
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-300/20 to-blue-400/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">
              AAROHAN
            </h1>
            <p className="text-xs text-white/70">
              Student Success Platform
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2 mt-3 px-2 py-1 bg-white/10 rounded-md">
          <Shield className="w-3 h-3 text-white/70" />
          <span className="text-xs text-white/70">Government of Rajasthan | 25102</span>
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
    </div>
  );
};

export default Sidebar;