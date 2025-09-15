import React from 'react';
import { User, Mail, Shield, Calendar, Activity, Clock, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">User Profile</h1>
        <p className="text-muted-foreground mt-2">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Info */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5 text-primary" />
              <span>Profile Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center space-x-4">
              <Avatar className="w-20 h-20 border-4 border-primary/20">
                <AvatarImage src="/assets/profiel.jpeg" alt="Profile photo" />
                <AvatarFallback className="bg-gradient-primary text-white text-lg">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="text-2xl font-semibold">{user?.username || 'User'}</h3>
                <p className="text-muted-foreground">Academic Counselor & Risk Analyst</p>
                <Badge variant="secondary" className="mt-2">
                  <Shield className="w-3 h-3 mr-1" />
                  Authorized Personnel
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>Email</span>
                </label>
                <p className="text-lg">{user?.username}@university.edu</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground flex items-center space-x-2">
                  <Shield className="w-4 h-4" />
                  <span>Role</span>
                </label>
                <Badge variant="secondary" className="bg-primary/10 text-primary">
                  Academic Counselor
                </Badge>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Member Since</span>
                </label>
                <p className="text-lg">January 2024</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Department</label>
                <p className="text-lg">Directorate of Technical Education</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Activity Stats */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-primary" />
                <span>Activity Overview</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm text-muted-foreground">Last Login</p>
                    <Clock className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <p className="font-medium">Today, 9:30 AM</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Sessions Today</p>
                  <p className="text-2xl font-bold text-primary">3</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Students Reviewed</p>
                  <p className="text-2xl font-bold text-success">12</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Simulations Run</p>
                  <p className="text-2xl font-bold text-accent">8</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                <span>System Permissions</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">View Students</span>
                  <Badge variant="secondary" className="bg-success/10 text-success">
                    ✓ Enabled
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Run Simulations</span>
                  <Badge variant="secondary" className="bg-success/10 text-success">
                    ✓ Enabled
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Export Data</span>
                  <Badge variant="secondary" className="bg-warning/10 text-warning">
                    ⚠ Limited
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Admin Access</span>
                  <Badge variant="secondary" className="bg-muted text-muted-foreground">
                    ✗ Disabled
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Usage Statistics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Usage This Month</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Dashboard Views</span>
                  <span>45/100</span>
                </div>
                <Progress value={45} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Simulations</span>
                  <span>23/50</span>
                </div>
                <Progress value={46} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Profile;