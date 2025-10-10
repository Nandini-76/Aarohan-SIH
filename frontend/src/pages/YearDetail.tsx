import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ChevronLeft,
  Users,
  TrendingUp,
  AlertTriangle,
  BookOpen,
  Calendar,
  Award,
  Search,
  Download,
  Filter
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import SiteHeader from '../components/SiteHeader';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import { useToast } from '../hooks/use-toast';

interface YearData {
  department: string;
  year: number;
  totalStudents: number;
  avgCgpa: number;
  avgAttendance: number;
  avgBacklogs: number;
  riskDistribution: {
    critical: number;
    atRisk: number;
    monitor: number;
    safe: number;
  };
}

interface SectionData {
  name: string;
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

interface Student {
  enrollmentNo: string;
  name: string;
  section: string;
  cgpa: number;
  attendance: number;
  backlogs: number;
  riskPhase: string;
  status: string;
}

interface AnalyticsData {
  cgpaHistogram: Array<{ range: string; count: number }>;
  attendanceByPhase: Record<string, number>;
  riskTrend: {
    labels: string[];
    values: number[];
  };
}

const RISK_COLORS = {
  critical: '#ef4444',
  atRisk: '#f97316',
  monitor: '#eab308',
  safe: '#22c55e',
};

const YearDetail: React.FC = () => {
  const { deptId, yearNo } = useParams<{ deptId: string; yearNo: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [yearData, setYearData] = useState<YearData | null>(null);
  const [sections, setSections] = useState<SectionData[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Section detail modal
  const [selectedSection, setSelectedSection] = useState<SectionData | null>(null);
  const [sectionStudents, setSectionStudents] = useState<Student[]>([]);
  const [isSectionModalOpen, setIsSectionModalOpen] = useState(false);
  const [loadingSectionStudents, setLoadingSectionStudents] = useState(false);

  // Filters for section student table
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('');

  useEffect(() => {
    fetchYearData();
  }, [deptId, yearNo]);

  const fetchYearData = async () => {
    setIsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/departments/${deptId}/years/${yearNo}`);

      if (!response.ok) {
        throw new Error('Failed to fetch year data');
      }

      const data = await response.json();
      setYearData(data.year);
      setSections(data.sections);
      setAnalytics(data.analytics);
    } catch (error) {
      console.error('Error fetching year data:', error);
      toast({
        title: "Error",
        description: "Failed to load year data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSectionStudents = async (sectionName: string) => {
    setLoadingSectionStudents(true);
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const params = new URLSearchParams();
      params.append('section', sectionName);
      if (filterRisk) params.append('risk', filterRisk);
      if (searchTerm) params.append('search', searchTerm);

      const response = await fetch(
        `${apiUrl}/api/departments/${deptId}/years/${yearNo}/students?${params}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch students');
      }

      const data = await response.json();
      setSectionStudents(data.students);
    } catch (error) {
      console.error('Error fetching students:', error);
      toast({
        title: "Error",
        description: "Failed to load student data",
        variant: "destructive",
      });
    } finally {
      setLoadingSectionStudents(false);
    }
  };

  const handleSectionClick = (section: SectionData) => {
    setSelectedSection(section);
    setIsSectionModalOpen(true);
    setSearchTerm('');
    setFilterRisk('');
    fetchSectionStudents(section.name);
  };

  const getRiskChartData = () => {
    if (!yearData) return [];
    const { riskDistribution } = yearData;
    return [
      { name: 'Critical', value: riskDistribution.critical, color: RISK_COLORS.critical },
      { name: 'At Risk', value: riskDistribution.atRisk, color: RISK_COLORS.atRisk },
      { name: 'Monitor', value: riskDistribution.monitor, color: RISK_COLORS.monitor },
      { name: 'Safe', value: riskDistribution.safe, color: RISK_COLORS.safe },
    ];
  };

  const getRiskBadgeColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'red':
        return 'destructive';
      case 'orange':
        return 'default';
      case 'yellow':
        return 'secondary';
      case 'green':
        return 'outline';
      default:
        return 'default';
    }
  };

  const exportSectionToCSV = () => {
    if (sectionStudents.length === 0) {
      toast({
        title: "No Data",
        description: "No students to export",
        variant: "default",
      });
      return;
    }

    const headers = ['Enrollment No', 'Name', 'Section', 'CGPA', 'Attendance', 'Backlogs', 'Risk Phase', 'Status'];
    const csvContent = [
      headers.join(','),
      ...sectionStudents.map(s =>
        [s.enrollmentNo, s.name, s.section, s.cgpa, s.attendance, s.backlogs, s.riskPhase, s.status].join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${deptId}_year${yearNo}_section${selectedSection?.name}_students.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast({
      title: "Export Successful",
      description: `Exported ${sectionStudents.length} students to CSV`,
      variant: "default",
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <SiteHeader />
        <div className="container mx-auto px-4 py-8">
          <Skeleton className="h-12 w-96 mb-6" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (!yearData) {
    return (
      <div className="min-h-screen bg-background">
        <SiteHeader />
        <div className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="p-12 text-center">
              <AlertTriangle className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-xl text-muted-foreground">Year data not found</p>
              <Button onClick={() => navigate(-1)} className="mt-4">
                Go Back
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb Navigation */}
        <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
          <Link to="/dashboard" className="hover:text-primary transition-colors">
            Dashboard
          </Link>
          <span>/</span>
          <Link
            to={`/department/${deptId}`}
            className="hover:text-primary transition-colors"
          >
            {yearData.department}
          </Link>
          <span>/</span>
          <span className="text-foreground font-medium">Year {yearNo}</span>
        </nav>

        {/* Back Button & Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => navigate(-1)}
              className="rounded-full"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-4xl font-bold">
                {yearData.department} - Year {yearNo}
              </h1>
              <p className="text-muted-foreground mt-1">
                Detailed analytics and student performance
              </p>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Students</p>
                    <p className="text-3xl font-bold mt-1">{yearData.totalStudents}</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <Users className="h-6 w-6 text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Avg CGPA</p>
                    <p className="text-3xl font-bold mt-1">{yearData.avgCgpa.toFixed(2)}</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                    <Award className="h-6 w-6 text-blue-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Avg Attendance</p>
                    <p className="text-3xl font-bold mt-1">{yearData.avgAttendance.toFixed(1)}%</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                    <Calendar className="h-6 w-6 text-green-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">At Risk</p>
                    <p className="text-3xl font-bold mt-1 text-red-500">
                      {yearData.riskDistribution.critical + yearData.riskDistribution.atRisk}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-red-500/10 flex items-center justify-center">
                    <AlertTriangle className="h-6 w-6 text-red-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Tabs Section */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="sections">Sections</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Risk Distribution Pie Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Risk Distribution</CardTitle>
                  <CardDescription>Student risk categories breakdown</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={getRiskChartData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => `${entry.name}: ${entry.value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getRiskChartData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* CGPA Distribution */}
              {analytics && (
                <Card>
                  <CardHeader>
                    <CardTitle>CGPA Distribution</CardTitle>
                    <CardDescription>Student distribution by CGPA range</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={analytics.cgpaHistogram}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="range" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* Attendance by Risk Phase */}
              {analytics && analytics.attendanceByPhase && (
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle>Attendance by Risk Phase</CardTitle>
                    <CardDescription>Average attendance for each risk category</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={Object.entries(analytics.attendanceByPhase).map(([phase, attendance]) => ({
                          phase,
                          attendance,
                        }))}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="phase" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="attendance" fill="#22c55e" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Sections Tab */}
          <TabsContent value="sections" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sections.map((section, index) => (
                <motion.div
                  key={section.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card 
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => handleSectionClick(section)}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>Section {section.name}</span>
                        <Badge variant="secondary">{section.studentCount} students</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {/* Metrics */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm text-muted-foreground">Avg CGPA</p>
                            <p className="text-2xl font-bold">{section.avgCgpa.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Attendance</p>
                            <p className="text-2xl font-bold">{section.avgAttendance.toFixed(1)}%</p>
                          </div>
                        </div>

                        {/* Risk Badges */}
                        <div className="flex flex-wrap gap-2">
                          <Badge variant="destructive" className="text-xs">
                            {section.riskDistribution.critical} Critical
                          </Badge>
                          <Badge className="bg-orange-500 hover:bg-orange-600 text-xs">
                            {section.riskDistribution.atRisk} At Risk
                          </Badge>
                          <Badge className="bg-yellow-500 hover:bg-yellow-600 text-black text-xs">
                            {section.riskDistribution.monitor} Monitor
                          </Badge>
                          <Badge className="bg-green-500 hover:bg-green-600 text-xs">
                            {section.riskDistribution.safe} Safe
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Section Detail Modal */}
        <Dialog open={isSectionModalOpen} onOpenChange={setIsSectionModalOpen}>
          <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between">
                <span>Section {selectedSection?.name} - Detail View</span>
                <Button variant="outline" size="sm" onClick={exportSectionToCSV}>
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </DialogTitle>
              <DialogDescription>
                {selectedSection && (
                  <div className="flex gap-6 mt-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Students</p>
                      <p className="text-2xl font-bold">{selectedSection.studentCount}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Avg CGPA</p>
                      <p className="text-2xl font-bold">{selectedSection.avgCgpa.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Avg Attendance</p>
                      <p className="text-2xl font-bold">{selectedSection.avgAttendance.toFixed(1)}%</p>
                    </div>
                  </div>
                )}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 mt-4">
              {/* Section Risk Chart */}
              {selectedSection && (
                <Card>
                  <CardHeader>
                    <CardTitle>Risk Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Critical', value: selectedSection.riskDistribution.critical, color: RISK_COLORS.critical },
                            { name: 'At Risk', value: selectedSection.riskDistribution.atRisk, color: RISK_COLORS.atRisk },
                            { name: 'Monitor', value: selectedSection.riskDistribution.monitor, color: RISK_COLORS.monitor },
                            { name: 'Safe', value: selectedSection.riskDistribution.safe, color: RISK_COLORS.safe },
                          ]}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={(entry) => `${entry.name}: ${entry.value}`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {[
                            { name: 'Critical', value: selectedSection.riskDistribution.critical, color: RISK_COLORS.critical },
                            { name: 'At Risk', value: selectedSection.riskDistribution.atRisk, color: RISK_COLORS.atRisk },
                            { name: 'Monitor', value: selectedSection.riskDistribution.monitor, color: RISK_COLORS.monitor },
                            { name: 'Safe', value: selectedSection.riskDistribution.safe, color: RISK_COLORS.safe },
                          ].map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* Filters */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Search by name or enrollment..."
                          value={searchTerm}
                          onChange={(e) => {
                            setSearchTerm(e.target.value);
                            if (selectedSection) fetchSectionStudents(selectedSection.name);
                          }}
                          className="pl-10"
                        />
                      </div>
                    </div>
                    <Select 
                      value={filterRisk} 
                      onValueChange={(value) => {
                        setFilterRisk(value);
                        if (selectedSection) fetchSectionStudents(selectedSection.name);
                      }}
                    >
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="All Risks" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All Risks</SelectItem>
                        <SelectItem value="Red">Critical</SelectItem>
                        <SelectItem value="Orange">At Risk</SelectItem>
                        <SelectItem value="Yellow">Monitor</SelectItem>
                        <SelectItem value="Green">Safe</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Student Table */}
              <Card>
                <CardHeader>
                  <CardTitle>Students ({sectionStudents.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  {loadingSectionStudents ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="text-center">
                        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                        <p className="text-muted-foreground">Loading students...</p>
                      </div>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-3 px-4 font-semibold">Enrollment No</th>
                            <th className="text-left py-3 px-4 font-semibold">Name</th>
                            <th className="text-left py-3 px-4 font-semibold">CGPA</th>
                            <th className="text-left py-3 px-4 font-semibold">Attendance</th>
                            <th className="text-left py-3 px-4 font-semibold">Backlogs</th>
                            <th className="text-left py-3 px-4 font-semibold">Risk</th>
                            <th className="text-left py-3 px-4 font-semibold">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sectionStudents.map((student, index) => (
                            <tr
                              key={student.enrollmentNo}
                              className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                              onClick={() => {
                                setIsSectionModalOpen(false);
                                navigate(`/student/${student.enrollmentNo}`);
                              }}
                            >
                              <td className="py-3 px-4 font-mono text-sm">{student.enrollmentNo}</td>
                              <td className="py-3 px-4">{student.name}</td>
                              <td className="py-3 px-4">
                                <span className="font-semibold">{student.cgpa.toFixed(2)}</span>
                              </td>
                              <td className="py-3 px-4">{student.attendance.toFixed(1)}%</td>
                              <td className="py-3 px-4">
                                <Badge variant={student.backlogs > 0 ? 'destructive' : 'outline'}>
                                  {student.backlogs}
                                </Badge>
                              </td>
                              <td className="py-3 px-4">
                                <Badge variant={getRiskBadgeColor(student.riskPhase)}>
                                  {student.riskPhase}
                                </Badge>
                              </td>
                              <td className="py-3 px-4">
                                <Badge variant="secondary">{student.status}</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>

                      {sectionStudents.length === 0 && !loadingSectionStudents && (
                        <div className="text-center py-12">
                          <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                          <p className="text-muted-foreground">No students found</p>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default YearDetail;
