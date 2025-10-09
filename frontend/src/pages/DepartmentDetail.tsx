import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ChevronLeft, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  ArrowRight 
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import SiteHeader from '../components/SiteHeader';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { useToast } from '../hooks/use-toast';

interface DepartmentData {
  id: string;
  name: string;
  totalStudents: number;
  avgCgpa: number;
  avgAttendance: number;
  riskDistribution: {
    critical: number;
    atRisk: number;
    monitor: number;
    safe: number;
  };
}

interface YearData {
  year: number;
  studentCount: number;
  avgCgpa: number;
  avgAttendance: number;
  riskDistribution: {
    critical: number;
    atRisk: number;
    monitor: number;
    safe: number;
  };
}

interface AnalyticsData {
  cgpaDistribution: Array<{ range: string; count: number }>;
  attendanceDistribution: Array<{ range: string; count: number }>;
  yearComparison: Array<{
    year: number;
    avgCgpa: number;
    avgAttendance: number;
    atRiskCount: number;
  }>;
}

const COLORS = {
  critical: '#ef4444',
  atRisk: '#f97316',
  monitor: '#eab308',
  safe: '#22c55e',
};

const DepartmentDetail: React.FC = () => {
  const { deptId } = useParams<{ deptId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [department, setDepartment] = useState<DepartmentData | null>(null);
  const [years, setYears] = useState<YearData[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDepartmentData();
  }, [deptId]);

  const fetchDepartmentData = async () => {
    setIsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/departments/${deptId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch department data');
      }
      
      const data = await response.json();
      setDepartment(data.department);
      setYears(data.years);
      setAnalytics(data.analytics);
    } catch (error) {
      console.error('Error fetching department data:', error);
      toast({
        title: "Error",
        description: "Failed to load department data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskChartData = (risk: any) => [
    { name: 'Critical', value: risk.critical, color: COLORS.critical },
    { name: 'At Risk', value: risk.atRisk, color: COLORS.atRisk },
    { name: 'Monitor', value: risk.monitor, color: COLORS.monitor },
    { name: 'Safe', value: risk.safe, color: COLORS.safe },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <SiteHeader />
        <div className="container mx-auto px-4 py-8">
          <Skeleton className="h-12 w-64 mb-6" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!department) {
    return (
      <div className="min-h-screen bg-background">
        <SiteHeader />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Department Not Found</h2>
            <Button onClick={() => navigate('/dashboard')}>
              <ChevronLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
          <Link to="/dashboard" className="hover:text-foreground">Dashboard</Link>
          <span>/</span>
          <span className="text-foreground font-medium">{department.name}</span>
        </div>

        {/* Header with Back Button */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="outline"
            size="icon"
            onClick={() => navigate('/dashboard')}
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-4xl font-bold">{department.name}</h1>
            <p className="text-muted-foreground mt-1">
              {department.totalStudents} students enrolled
            </p>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
                  <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Students</p>
                  <p className="text-2xl font-bold">{department.totalStudents}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
                  <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg CGPA</p>
                  <p className="text-2xl font-bold">{department.avgCgpa.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
                  <TrendingUp className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg Attendance</p>
                  <p className="text-2xl font-bold">{department.avgAttendance.toFixed(0)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-orange-100 dark:bg-orange-900 rounded-full">
                  <AlertTriangle className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">At Risk</p>
                  <p className="text-2xl font-bold">
                    {department.riskDistribution.critical + department.riskDistribution.atRisk}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Year Cards */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Year-wise Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {years.map((year) => (
              <Link key={year.year} to={`/department/${deptId}/year/${year.year}`}>
                <motion.div
                  whileHover={{ scale: 1.02, y: -4 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card className="cursor-pointer hover:shadow-lg transition-all duration-300 border-2 hover:border-primary">
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center justify-between">
                        <span>Year {year.year}</span>
                        <ArrowRight className="h-5 w-5 text-muted-foreground" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold mb-3">{year.studentCount} Students</p>
                      
                      <div className="space-y-2 text-sm mb-3">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Avg CGPA:</span>
                          <span className="font-semibold">{year.avgCgpa}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Attendance:</span>
                          <span className="font-semibold">{year.avgAttendance}%</span>
                        </div>
                      </div>
                      
                      <div className="flex gap-1 flex-wrap">
                        {year.riskDistribution.critical > 0 && (
                          <Badge variant="destructive" className="text-xs px-1.5 py-0.5">
                            {year.riskDistribution.critical}
                          </Badge>
                        )}
                        {year.riskDistribution.atRisk > 0 && (
                          <Badge className="text-xs px-1.5 py-0.5 bg-orange-500">
                            {year.riskDistribution.atRisk}
                          </Badge>
                        )}
                        {year.riskDistribution.monitor > 0 && (
                          <Badge className="text-xs px-1.5 py-0.5 bg-yellow-500 text-black">
                            {year.riskDistribution.monitor}
                          </Badge>
                        )}
                        {year.riskDistribution.safe > 0 && (
                          <Badge className="text-xs px-1.5 py-0.5 bg-green-500">
                            {year.riskDistribution.safe}
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </Link>
            ))}
          </div>
        </div>

        {/* Analytics Section */}
        {analytics && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Distribution Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getRiskChartData(department.riskDistribution)}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {getRiskChartData(department.riskDistribution).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Year Comparison Bar Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Year-wise CGPA Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analytics.yearComparison}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" label={{ value: 'Year', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Avg CGPA', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey="avgCgpa" fill="#3b82f6" name="Avg CGPA" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default DepartmentDetail;
