import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate, useLocation } from 'react-router-dom';
import { Search, Users, AlertTriangle, CheckCircle, XCircle, RefreshCw, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { studentApi } from '../services/api';
import { Student, DashboardStats } from '../types';
import { useToast } from '../hooks/use-toast';
import { cn } from '@/lib/utils';
import { useAuth } from '../contexts/AuthContext';
import SiteHeader from '@/components/SiteHeader';

const Dashboard: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  const [students, setStudents] = useState<Student[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [attendanceBins, setAttendanceBins] = useState<{ range: string; count: number }[]>([]);
  const [cgpaBins, setCgpaBins] = useState<{ range: string; count: number }[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    const filtered = students.filter(student =>
      student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.enrollment_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.department?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredStudents(filtered);
  }, [students, searchTerm]);

  const fetchStudents = async () => {
    try {
      setIsLoading(true);
      const data = await studentApi.getAllStudents();
  setStudents(data);
  calculateStats(data);
  buildCharts(data);
    } catch (error) {
      console.error('Failed to fetch students:', error);
      toast({
        title: "Error",
        description: "Failed to fetch students data. Please check if the backend server is running.",
        variant: "destructive",
      });
      // Fallback to empty array on error
      setStudents([]);
      setStats(null);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      setIsRefreshing(true);
      await fetchStudents();
      toast({
        title: "Data Refreshed",
        description: "Student data has been updated successfully.",
      });
    } catch (error) {
      toast({
        title: "Refresh Failed",
        description: "Failed to refresh data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  const calculateStats = (studentData: Student[]) => {
    const stats: DashboardStats = {
      total_students: studentData.length,
      green_count: studentData.filter(s => s.phase === "Green").length,
      yellow_count: studentData.filter(s => s.phase === "Yellow").length,
      orange_count: studentData.filter(s => s.phase === "Orange").length,
      red_count: studentData.filter(s => s.phase === "Red").length,
      monitor_count: 0,
      at_risk_count: 0
    };
    // To Monitor = Yellow; At Risk = Orange
    stats.monitor_count = stats.yellow_count;
    stats.at_risk_count = stats.orange_count;
    setStats(stats);
  };

  const buildCharts = (studentData: Student[]) => {
    // Attendance bins: 0-60, 60-70, 70-80, 80-90, 90-100
    const attEdges = [0, 60, 70, 80, 90, 100];
    const attCounts = Array(attEdges.length - 1).fill(0);
    studentData.forEach(s => {
      const a = Math.max(0, Math.min(100, Number(s.attendance) || 0));
      const idx = Math.max(0, Math.min(attCounts.length - 1, attEdges.findIndex((e, i) => a >= e && a < attEdges[i + 1])));
      attCounts[idx]++;
    });
    const attData = attCounts.map((c, i) => ({ range: `${attEdges[i]}-${attEdges[i + 1]}`, count: c }));
    setAttendanceBins(attData);

    // CGPA bins: 0-5, 5-6.5, 6.5-8, 8-9, 9-10
    const gEdges = [0, 5, 6.5, 8, 9, 10];
    const gCounts = Array(gEdges.length - 1).fill(0);
    studentData.forEach(s => {
      const g = Math.max(0, Math.min(10, Number(s.cgpa) || 0));
      const idx = Math.max(0, Math.min(gCounts.length - 1, gEdges.findIndex((e, i) => g >= e && g < gEdges[i + 1])));
      gCounts[idx]++;
    });
    const gData = gCounts.map((c, i) => ({ range: `${gEdges[i]}-${gEdges[i + 1]}`, count: c }));
    setCgpaBins(gData);
  };
  const handleStudentClick = (enrollmentNo: string) => {
    navigate(`/student/${enrollmentNo}`);
  };

  const statCards = stats ? [
    {
      title: "Total Students",
      value: stats.total_students,
      icon: Users,
      color: "text-primary",
      bgColor: "bg-primary/10"
    },
    {
      title: "Safe (Green)", 
      value: stats.green_count,
      icon: CheckCircle,
      color: "text-success",
      bgColor: "bg-success/10"
    },
    {
      title: "To Monitor (Yellow)",
      value: stats.monitor_count,
      icon: AlertTriangle,
      color: "text-yellow-500",
      bgColor: "bg-yellow-500/10"
    },
    {
      title: "At Risk (Orange)",
      value: stats.at_risk_count,
      icon: XCircle,
      color: "text-orange-500",
      bgColor: "bg-orange-500/10"
    },
    {
      title: "Critical (Red)",
      value: stats.red_count,
      icon: XCircle,
      color: "text-red-500",
      bgColor: "bg-red-500/10"
    }
  ] : [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" text="Loading dashboard data..." />
      </div>
    );
  }

  const bgStyle: React.CSSProperties = {
    background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                 radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                 linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
  };

  return (
    <div className="min-h-screen text-white" style={bgStyle}>
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold [text-shadow:_0_3px_0_rgba(0,0,0,.25)]">Student Guardian Dashboard</h1>
          <p className="text-white/90 mt-2">
            Monitor student risk levels and academic performance
          </p>
        </div>
        <Button 
          onClick={refreshData}
          disabled={isRefreshing}
          variant="outline"
          className="flex items-center space-x-2"
        >
          <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Stats Cards */}
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-elegant transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <p className="text-3xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={cn("p-3 rounded-full", stat.bgColor)}>
                  <stat.icon className={cn("h-6 w-6", stat.color)} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="col-span-1 lg:col-span-2">
          <CardHeader>
            <CardTitle>Attendance Distribution (%)</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={attendanceBins} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                <Bar dataKey="count" fill="#60a5fa" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: 'Green', value: stats?.green_count || 0, color: '#22c55e' },
                    { name: 'To Monitor (Yellow)', value: stats?.yellow_count || 0, color: '#eab308' },
                    { name: 'At Risk (Orange)', value: stats?.orange_count || 0, color: '#fb923c' },
                    { name: 'Critical (Red)', value: stats?.red_count || 0, color: '#ef4444' },
                  ]}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={40}
                  outerRadius={60}
                  paddingAngle={2}
                >
                  {['#22c55e','#eab308','#fb923c','#ef4444'].map((c, i) => (
                    <Cell key={i} fill={c} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>CGPA Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cgpaBins} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                <Bar dataKey="count" fill="#a78bfa" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Quick Actions */}
      <div className="flex flex-wrap gap-3">
        <Button 
          onClick={() => navigate('/simulation')}
          className="bg-gradient-secondary hover:opacity-90"
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          Run Simulation
        </Button>
      </div>
      </div>
      {/* Students Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
            <div>
              <CardTitle>Students Overview</CardTitle>
              <p className="text-sm text-white/85 mt-1">
                {filteredStudents.length} of {students.length} students
              </p>
            </div>
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="Search students..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredStudents.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
              <p className="text-muted-foreground">
                {searchTerm ? 'No students found matching your search.' : 'No students data available.'}
              </p>
              {searchTerm && (
                <Button 
                  variant="ghost" 
                  onClick={() => setSearchTerm('')}
                  className="mt-2"
                >
                  Clear search
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Enrollment No.</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Attendance</TableHead>
                  <TableHead>CGPA</TableHead>
                  <TableHead>Backlogs</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead className="max-w-xs">Risk Factors</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredStudents.map((student) => (
                  <TableRow
                    key={student.enrollment_no}
                    className="cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => handleStudentClick(student.enrollment_no)}
                  >
                    <TableCell className="font-medium">
                      {student.enrollment_no}
                    </TableCell>
                    <TableCell className="font-medium">{student.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{student.department || "N/A"}</Badge>
                    </TableCell>
                    <TableCell>
                      <span className={cn(
                        "font-medium",
                        student.attendance < 70 ? "text-destructive" : 
                        student.attendance < 80 ? "text-warning" : "text-success"
                      )}>
                        {student.attendance}%
                      </span>
                    </TableCell>
                    <TableCell>{student.cgpa}</TableCell>
                    <TableCell>
                      <span className={cn(
                        "font-medium",
                        student.backlogs > 3 ? "text-destructive" : 
                        student.backlogs > 0 ? "text-warning" : "text-success"
                      )}>
                        {student.backlogs}
                      </span>
                    </TableCell>
                    <TableCell>
                      <RiskBadge 
                        phase={student.phase || "Green"} 
                        showIcon={student.phase === "Red" || student.phase === "Orange"}
                      />
                    </TableCell>
                    <TableCell className="max-w-xs truncate text-muted-foreground">
                      {student.risk_reason || "No specific risk factors"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            </div>
          )}
        </CardContent>
      </Card>
      </main>
    </div>
  );
};

export default Dashboard;