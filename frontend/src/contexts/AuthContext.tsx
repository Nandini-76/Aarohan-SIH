import React, { createContext, useContext } from 'react';
import { AuthContextType } from '../types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Always return authenticated state since authentication is removed
  const isAuthenticated = true;
  const user = { username: 'User' };

  const login = async (username: string, password: string): Promise<boolean> => {
    // No-op function since authentication is disabled
    return true;
  };

  const logout = () => {
    // No-op function since authentication is disabled
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, user }}>
      {children}
    </AuthContext.Provider>
  );
};