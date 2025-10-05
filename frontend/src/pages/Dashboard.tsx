import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Search, Users, AlertTriangle, CheckCircle, XCircle, TrendingUp, Filter, AlertOctagon } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { Skeleton, TableSkeleton, StatCardSkeleton } from '../components/ui/skeleton';
import { studentApi } from '../services/api';
import { Student, DashboardStats } from '../types';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';
import SiteHeader from '../components/SiteHeader';
import { motion, AnimatePresence } from 'framer-motion';

const Dashboard: React.FC = () => {
  // Filter state
  const [showFilter, setShowFilter] = useState(false);
  const [filterDepartment, setFilterDepartment] = useState('');
  const [filterAttendance, setFilterAttendance] = useState('');
  const [filterCgpa, setFilterCgpa] = useState('');
  const [filterBacklogs, setFilterBacklogs] = useState('');
  const [filterRisk, setFilterRisk] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [attendanceBins, setAttendanceBins] = useState<{ range: string; count: number }[]>([]);
  const [cgpaBins, setCgpaBins] = useState<{ range: string; count: number }[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Ref for filter dropdown
  const filterRef = useRef<HTMLDivElement>(null);

  // Handle click outside filter
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
        setShowFilter(false);
      }
    };

    if (showFilter) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showFilter]);

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    let filtered = students.filter(student =>
      student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.enrollment_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.department?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Apply Department filter
    if (filterDepartment) {
      filtered = filtered.filter(s => s.department === filterDepartment);
    }
    // Apply Attendance filter
    if (filterAttendance) {
      if (filterAttendance === '<60') filtered = filtered.filter(s => s.attendance < 60);
      if (filterAttendance === '60-75') filtered = filtered.filter(s => s.attendance >= 60 && s.attendance < 75);
      if (filterAttendance === '>=75') filtered = filtered.filter(s => s.attendance >= 75);
    }
    // Apply CGPA filter
    if (filterCgpa) {
      if (filterCgpa === '<6') filtered = filtered.filter(s => s.cgpa < 6);
      if (filterCgpa === '6-8') filtered = filtered.filter(s => s.cgpa >= 6 && s.cgpa < 8);
      if (filterCgpa === '>=8') filtered = filtered.filter(s => s.cgpa >= 8);
    }
    // Apply Backlogs filter
    if (filterBacklogs) {
      if (filterBacklogs === '0') filtered = filtered.filter(s => s.backlogs === 0);
      if (filterBacklogs === '1-2') filtered = filtered.filter(s => s.backlogs >= 1 && s.backlogs <= 2);
      if (filterBacklogs === '>=3') filtered = filtered.filter(s => s.backlogs >= 3);
    }
    // Apply Risk Level filter
    if (filterRisk) {
      filtered = filtered.filter(s => (s.phase || s.final_phase) === filterRisk);
    }

    // Sort by risk level: Red → Orange → Yellow → Green
    const riskPriority = { 'Red': 1, 'Orange': 2, 'Yellow': 3, 'Green': 4 };
    const sortedFiltered = filtered.sort((a, b) => {
      const phaseA = a.phase || a.final_phase || 'Green';
      const phaseB = b.phase || b.final_phase || 'Green';
      const priorityA = riskPriority[phaseA as keyof typeof riskPriority] || 5;
      const priorityB = riskPriority[phaseB as keyof typeof riskPriority] || 5;
      if (priorityA !== priorityB) {
        return priorityA - priorityB;
      }
      return a.enrollment_no.localeCompare(b.enrollment_no);
    });
    setFilteredStudents(sortedFiltered);
  }, [students, searchTerm, filterDepartment, filterAttendance, filterCgpa, filterBacklogs, filterRisk]);

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

  const calculateStats = (studentData: Student[]) => {
    const stats: DashboardStats = {
      total_students: studentData.length,
      green_count: studentData.filter(s => (s.final_phase || s.phase) === "Green").length,
      yellow_count: studentData.filter(s => (s.final_phase || s.phase) === "Yellow").length,
      orange_count: studentData.filter(s => (s.final_phase || s.phase) === "Orange").length,
      red_count: studentData.filter(s => (s.final_phase || s.phase) === "Red").length,
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
      bgColor: "bg-primary/10",
      borderColor: "border-primary/20",
      hoverColor: "hover:bg-primary/15"
    },
    {
      title: "Safe (Green)", 
      value: stats.green_count,
      icon: CheckCircle,
      color: "text-emerald-600",
      bgColor: "bg-emerald-50",
      borderColor: "border-emerald-200",
      hoverColor: "hover:bg-emerald-100",
      glowColor: "hover:shadow-emerald-200/50"
    },
    {
      title: "To Monitor (Yellow)",
      value: stats.monitor_count,
      icon: AlertTriangle,
      color: "text-amber-600",
      bgColor: "bg-amber-50",
      borderColor: "border-amber-200",
      hoverColor: "hover:bg-amber-100",
      glowColor: "hover:shadow-amber-200/50"
    },
    {
      title: "At Risk (Orange)",
      value: stats.at_risk_count,
      icon: AlertOctagon,
      color: "text-orange-700",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-200",
      hoverColor: "hover:bg-orange-100",
      glowColor: "hover:shadow-orange-200/50"
    },
    {
      title: "Critical (Red)",
      value: stats.red_count,
      icon: XCircle,
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
      hoverColor: "hover:bg-red-100",
      glowColor: "hover:shadow-red-200/50",
      pulse: stats.red_count > 0
    }
  ] : [];

  if (isLoading) {
    return (
      <motion.div 
        className="min-h-screen text-white" 
        style={{
          background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                       radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                       linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <SiteHeader />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header skeleton */}
          <div className="mb-8">
            <Skeleton variant="text" className="h-8 w-64 mb-2 bg-white/20" />
            <Skeleton variant="text" className="h-5 w-96 bg-white/10" />
          </div>

          {/* Stats cards skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {Array.from({ length: 4 }).map((_, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <StatCardSkeleton />
              </motion.div>
            ))}
          </div>

          {/* Charts section skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <Skeleton variant="text" className="h-6 w-48 bg-white/20" />
                </CardHeader>
                <CardContent>
                  <Skeleton variant="card" className="h-64 bg-white/10" />
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <Skeleton variant="text" className="h-6 w-48 bg-white/20" />
                </CardHeader>
                <CardContent>
                  <Skeleton variant="card" className="h-64 bg-white/10" />
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Search and filter skeleton */}
          <motion.div
            className="mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <div className="flex gap-4 items-center">
              <Skeleton variant="text" className="flex-1 h-10 bg-white/10" />
              <Skeleton variant="button" className="bg-white/10" />
            </div>
          </motion.div>

          {/* Table skeleton */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <Skeleton variant="text" className="h-6 w-32 bg-white/20" />
              </CardHeader>
              <CardContent>
                <TableSkeleton rows={8} cols={6} />
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </motion.div>
    );
  }

  const bgStyle: React.CSSProperties = {
    background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                 radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                 linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
  };

  return (
    <motion.div 
      className="min-h-screen text-white" 
      style={bgStyle}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12 space-y-6">
      {/* Header */}
      <motion.div 
        className="flex items-center justify-between"
        initial={{ y: -30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div>
          <h1 className="text-3xl font-bold [text-shadow:_0_3px_0_rgba(0,0,0,.25)]">Student Guardian Dashboard</h1>
          <p className="text-white/90 mt-2">
            Monitor student risk levels and academic performance
          </p>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4"
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {statCards.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 + (index * 0.1) }}
            whileHover={{ scale: 1.05, y: -5 }}
            whileTap={{ scale: 0.98 }}
          >
            <Card className={cn(
              "relative overflow-hidden border-2 transition-all duration-300 cursor-pointer",
              stat.bgColor,
              stat.borderColor,
              stat.hoverColor,
              "hover:shadow-lg",
              stat.glowColor && `hover:shadow-lg ${stat.glowColor}`,
              stat.pulse && "animate-pulse"
            )}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <motion.p 
                      className={cn("text-2xl font-bold", stat.color)}
                      initial={{ scale: 0.8 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.3, delay: 0.5 + (index * 0.1) }}
                    >
                      {stat.value}
                    </motion.p>
                  </div>
                  <motion.div
                    className={cn("p-3 rounded-full", stat.bgColor)}
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <stat.icon className={cn("h-6 w-6", stat.color)} />
                  </motion.div>
                </div>
                {stat.pulse && (
                  <motion.div
                    className="absolute inset-0 bg-red-100/20 rounded-lg"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts */}
      <motion.div 
        className="grid grid-cols-1 lg:grid-cols-3 gap-4"
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <motion.div
          className="col-span-1 lg:col-span-2"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="hover:shadow-xl transition-all duration-300 border-0 bg-white/95 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-gray-800">Attendance Distribution (%)</CardTitle>
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
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="hover:shadow-xl transition-all duration-300 border-0 bg-white/95 backdrop-blur">
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
        </motion.div>
      </motion.div>

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
            <div className="flex gap-2 w-full sm:w-auto items-center">
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search students..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              {/* Filter Button and Dropdown */}
              <div className="relative" ref={filterRef}>
                <Button variant="outline" size="sm" onClick={() => setShowFilter(f => !f)}>
                  Filter
                </Button>
                {showFilter && (
                  <div className="absolute right-0 mt-2 w-72 bg-white text-black rounded-lg shadow-lg z-50 p-4 space-y-3 border border-gray-200">
                    {/* Department Filter */}
                    <div>
                      <label className="block text-xs font-semibold mb-1">Department</label>
                      <select className="w-full border rounded p-1" value={filterDepartment} onChange={e => setFilterDepartment(e.target.value)}>
                        <option value="">All</option>
                        {[...new Set(students.map(s => s.department).filter(Boolean))].map(dep => (
                          <option key={dep} value={dep}>{dep}</option>
                        ))}
                      </select>
                    </div>
                    {/* Attendance Filter */}
                    <div>
                      <label className="block text-xs font-semibold mb-1">Attendance</label>
                      <select className="w-full border rounded p-1" value={filterAttendance} onChange={e => setFilterAttendance(e.target.value)}>
                        <option value="">All</option>
                        <option value="<60">Below 60%</option>
                        <option value="60-75">60% - 75%</option>
                        <option value=">=75">75% and above</option>
                      </select>
                    </div>
                    {/* CGPA Filter */}
                    <div>
                      <label className="block text-xs font-semibold mb-1">CGPA</label>
                      <select className="w-full border rounded p-1" value={filterCgpa} onChange={e => setFilterCgpa(e.target.value)}>
                        <option value="">All</option>
                        <option value="<6">Below 6</option>
                        <option value="6-8">6 - 8</option>
                        <option value=">=8">8 and above</option>
                      </select>
                    </div>
                    {/* Backlogs Filter */}
                    <div>
                      <label className="block text-xs font-semibold mb-1">Backlogs</label>
                      <select className="w-full border rounded p-1" value={filterBacklogs} onChange={e => setFilterBacklogs(e.target.value)}>
                        <option value="">All</option>
                        <option value="0">0</option>
                        <option value="1-2">1 - 2</option>
                        <option value=">=3">3 or more</option>
                      </select>
                    </div>
                    {/* Risk Level Filter */}
                    <div>
                      <label className="block text-xs font-semibold mb-1">Risk Level</label>
                      <select className="w-full border rounded p-1" value={filterRisk} onChange={e => setFilterRisk(e.target.value)}>
                        <option value="">All</option>
                        <option value="Red">Red</option>
                        <option value="Orange">Orange</option>
                        <option value="Yellow">Yellow</option>
                        <option value="Green">Green</option>
                      </select>
                    </div>
                    <div className="flex justify-end gap-2 pt-2">
                      <Button size="sm" variant="secondary" onClick={() => { setFilterDepartment(''); setFilterAttendance(''); setFilterCgpa(''); setFilterBacklogs(''); setFilterRisk(''); }}>Clear</Button>
                      <Button size="sm" onClick={() => setShowFilter(false)}>Apply</Button>
                    </div>
                  </div>
                )}
              </div>
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
                        phase={(student.final_phase || student.phase) || "Green"} 
                        showIcon={(student.final_phase || student.phase) === "Red" || (student.final_phase || student.phase) === "Orange"}
                      />
                    </TableCell>
                    <TableCell className="max-w-xs truncate text-muted-foreground">
                      {student.risk_reason || student.override_reason || "No specific risk factors"}
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
    </motion.div>
  );
};

export default Dashboard;