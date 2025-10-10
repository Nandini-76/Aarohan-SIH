import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ChevronLeft,
  Users,
  Search,
  Download,
  TrendingUp,
  Calendar,
  Award,
  AlertTriangle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Skeleton } from '../components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import SiteHeader from '../components/SiteHeader';
import GlobalSearch from '../components/GlobalSearch';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import { useToast } from '../hooks/use-toast';

interface SectionData {
  name: string;
  studentCount: number;
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

const RISK_COLORS = {
  critical: '#ef4444',
  atRisk: '#f97316',
  monitor: '#eab308',
  safe: '#22c55e',
};

const SectionStudents: React.FC = () => {
  const { deptId, yearNo, sectionName } = useParams<{ deptId: string; yearNo: string; sectionName: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [sectionData, setSectionData] = useState<SectionData | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('all');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const studentsPerPage = 20;

  // Global search
  const [isGlobalSearchOpen, setIsGlobalSearchOpen] = useState(false);
  const [globalSearchTerm, setGlobalSearchTerm] = useState('');

  useEffect(() => {
    fetchSectionData();
  }, [deptId, yearNo, sectionName]);

  useEffect(() => {
    applyFilters();
  }, [students, searchTerm, filterRisk]);

  const fetchSectionData = async () => {
    setIsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const params = new URLSearchParams();
      params.append('section', sectionName || '');

      const response = await fetch(
        `${apiUrl}/api/departments/${deptId}/years/${yearNo}/students?${params}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch section data');
      }

      const data = await response.json();
      console.log('Section data received:', data);
      
      // Extract section metadata
      if (data.students && data.students.length > 0) {
        const sectionStudents = data.students;
        const critical = sectionStudents.filter((s: Student) => s.riskPhase === 'Red').length;
        const atRisk = sectionStudents.filter((s: Student) => s.riskPhase === 'Orange').length;
        const monitor = sectionStudents.filter((s: Student) => s.riskPhase === 'Yellow').length;
        const safe = sectionStudents.filter((s: Student) => s.riskPhase === 'Green').length;
        
        const avgCgpa = sectionStudents.reduce((sum: number, s: Student) => sum + s.cgpa, 0) / sectionStudents.length;
        const avgAttendance = sectionStudents.reduce((sum: number, s: Student) => sum + s.attendance, 0) / sectionStudents.length;
        const avgBacklogs = sectionStudents.reduce((sum: number, s: Student) => sum + s.backlogs, 0) / sectionStudents.length;
        
        setSectionData({
          name: sectionName || '',
          studentCount: sectionStudents.length,
          avgCgpa,
          avgAttendance,
          avgBacklogs,
          riskDistribution: { critical, atRisk, monitor, safe }
        });
      }
      
      setStudents(data.students || []);
    } catch (error) {
      console.error('Error fetching section data:', error);
      toast({
        title: "Error",
        description: "Failed to load section data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...students];

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        s => s.name.toLowerCase().includes(term) || 
             s.enrollmentNo.toLowerCase().includes(term)
      );
    }

    // Risk filter
    if (filterRisk && filterRisk !== 'all') {
      filtered = filtered.filter(s => s.riskPhase === filterRisk);
    }

    setFilteredStudents(filtered);
    setCurrentPage(1); // Reset to first page when filters change
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

  const getRiskBadgeStyle = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'orange':
        return { backgroundColor: '#f97316', color: 'white' };
      case 'yellow':
        return { backgroundColor: '#eab308', color: 'black' };
      case 'green':
        return { backgroundColor: '#22c55e', color: 'white' };
      default:
        return {};
    }
  };

  const exportToCSV = () => {
    if (filteredStudents.length === 0) {
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
      ...filteredStudents.map(s =>
        [s.enrollmentNo, s.name, s.section, s.cgpa, s.attendance, s.backlogs, s.riskPhase, s.status].join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${deptId}_year${yearNo}_section${sectionName}_students.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast({
      title: "Export Successful",
      description: `Exported ${filteredStudents.length} students to CSV`,
      variant: "default",
    });
  };

  const getRiskChartData = () => {
    if (!sectionData) return [];
    const { riskDistribution } = sectionData;
    return [
      { name: 'Critical', value: riskDistribution.critical, color: RISK_COLORS.critical },
      { name: 'At Risk', value: riskDistribution.atRisk, color: RISK_COLORS.atRisk },
      { name: 'Monitor', value: riskDistribution.monitor, color: RISK_COLORS.monitor },
      { name: 'Safe', value: riskDistribution.safe, color: RISK_COLORS.safe },
    ];
  };

  // Pagination
  const indexOfLastStudent = currentPage * studentsPerPage;
  const indexOfFirstStudent = indexOfLastStudent - studentsPerPage;
  const currentStudents = filteredStudents.slice(indexOfFirstStudent, indexOfLastStudent);
  const totalPages = Math.ceil(filteredStudents.length / studentsPerPage);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

  if (!sectionData) {
    return (
      <div className="min-h-screen bg-background">
        <SiteHeader />
        <div className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="p-12 text-center">
              <AlertTriangle className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-xl text-muted-foreground">Section data not found</p>
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
            {deptId?.toUpperCase().replace('_', ' ')}
          </Link>
          <span>/</span>
          <Link
            to={`/department/${deptId}/year/${yearNo}`}
            className="hover:text-primary transition-colors"
          >
            Year {yearNo}
          </Link>
          <span>/</span>
          <span className="text-foreground font-medium">Section {sectionName}</span>
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
                Section {sectionName}
              </h1>
              <p className="text-muted-foreground mt-1">
                {deptId?.toUpperCase().replace('_', ' ')} - Year {yearNo}
              </p>
            </div>
          </div>

          {/* Global Search */}
          <div className="relative w-80">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search students globally..."
              value={globalSearchTerm}
              onChange={(e) => setGlobalSearchTerm(e.target.value)}
              onFocus={() => setIsGlobalSearchOpen(true)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && globalSearchTerm.length >= 2) {
                  setIsGlobalSearchOpen(true);
                }
              }}
              className="pl-10 cursor-pointer"
              title="Click to open global search"
            />
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
                    <p className="text-3xl font-bold mt-1">{sectionData.studentCount}</p>
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
                    <p className="text-3xl font-bold mt-1">{sectionData.avgCgpa.toFixed(2)}</p>
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
                    <p className="text-3xl font-bold mt-1">{sectionData.avgAttendance.toFixed(1)}%</p>
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
                      {sectionData.riskDistribution.critical + sectionData.riskDistribution.atRisk}
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

        {/* Risk Distribution Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Student risk categories breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
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

          {/* Filters Card */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Student List</CardTitle>
                <Button variant="outline" size="sm" onClick={exportToCSV}>
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search by name or enrollment..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={filterRisk} onValueChange={setFilterRisk}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="All Risks" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Risks</SelectItem>
                    <SelectItem value="Red">Critical</SelectItem>
                    <SelectItem value="Orange">At Risk</SelectItem>
                    <SelectItem value="Yellow">Monitor</SelectItem>
                    <SelectItem value="Green">Safe</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Results info */}
              <div className="mt-4 text-sm text-muted-foreground">
                Showing {indexOfFirstStudent + 1}-{Math.min(indexOfLastStudent, filteredStudents.length)} of {filteredStudents.length} students
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Student Table */}
        <Card>
          <CardContent className="p-6">
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
                  {currentStudents.map((student) => (
                    <motion.tr
                      key={student.enrollmentNo}
                      className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/student/${student.enrollmentNo}`)}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      whileHover={{ backgroundColor: 'rgba(0,0,0,0.02)' }}
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
                        <Badge 
                          variant={getRiskBadgeColor(student.riskPhase)}
                          style={getRiskBadgeStyle(student.riskPhase)}
                        >
                          {student.riskPhase}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary">{student.status}</Badge>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>

              {currentStudents.length === 0 && (
                <div className="text-center py-12">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No students found</p>
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                
                <div className="flex gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                    // Show first page, last page, current page, and pages around current
                    if (
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1)
                    ) {
                      return (
                        <Button
                          key={page}
                          variant={page === currentPage ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => handlePageChange(page)}
                        >
                          {page}
                        </Button>
                      );
                    } else if (page === currentPage - 2 || page === currentPage + 2) {
                      return <span key={page} className="px-2">...</span>;
                    }
                    return null;
                  })}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Global Search Modal */}
      <GlobalSearch
        isOpen={isGlobalSearchOpen}
        onClose={() => setIsGlobalSearchOpen(false)}
        initialSearchTerm={globalSearchTerm}
      />
    </div>
  );
};

export default SectionStudents;
