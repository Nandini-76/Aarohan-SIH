import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, Database, TrendingUp, AlertTriangle } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { getAllStudentsFromFirebase, isFirebaseConfigured, listenToPath } from '../services/firebase';
import { Student } from '../types';
import { useToast } from '../hooks/use-toast';
import SiteHeader from '../components/SiteHeader';
import AnalyticsOverview from '../components/AnalyticsOverview';
import DepartmentSection from '../components/DepartmentSection';
import { Skeleton, StatCardSkeleton } from '../components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const DEPARTMENT_COLORS: Record<string, string> = {
  'BBA': '#3b82f6',
  'BSc': '#8b5cf6',
  'BSc Agriculture': '#10b981',
  'BTech': '#f59e0b',
  'B.B.A.': '#3b82f6',
  'B.Sc': '#8b5cf6',
  'B.Sc Agriculture': '#10b981',
  'B.Tech': '#f59e0b',
};

const DashboardNew: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPhase, setFilterPhase] = useState('');
  const [filterGender, setFilterGender] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'analytics' | 'departments'>('analytics');
  const [dataSource, setDataSource] = useState<'backend' | 'firebase' | null>(null);
  
  const navigate = useNavigate();
  const { toast } = useToast();

  // Fetch students from Firebase
  useEffect(() => {
    fetchStudents();
    
    // Set up real-time listener
    if (isFirebaseConfigured()) {
      const unsubscribe = listenToPath('students', (data) => {
        if (data) {
          const studentsArray = Object.values(data) as Student[];
          console.log(`Real-time update: ${studentsArray.length} students received from Firebase`);
          
          setStudents(studentsArray);
          setDataSource('firebase');
          
          // Show toast notification for recent updates
          const firstStudent = studentsArray[0] as any;
          if (firstStudent?.lastUpdated) {
            const updateTime = new Date(firstStudent.lastUpdated);
            const now = new Date();
            const secondsAgo = Math.floor((now.getTime() - updateTime.getTime()) / 1000);
            
            if (secondsAgo < 10) {
              toast({
                title: "Data Updated",
                description: "Backend has pushed fresh predictions to Firebase",
                variant: "default",
              });
            }
          }
        }
      });
      
      return () => {
        console.log('Cleaning up Firebase listener');
        unsubscribe();
      };
    }
  }, []);

  const fetchStudents = async () => {
    try {
      setIsLoading(true);
      
      if (!isFirebaseConfigured()) {
        throw new Error('Firebase not configured');
      }
      
      const firebaseData = await getAllStudentsFromFirebase();
      
      if (firebaseData && firebaseData.length > 0) {
        setStudents(firebaseData);
        setDataSource('firebase');
        
        // Check data freshness
        const firstStudent = firebaseData[0];
        const lastUpdated = firstStudent.lastUpdated;
        
        if (lastUpdated) {
          const updateTime = new Date(lastUpdated);
          const now = new Date();
          const minutesAgo = Math.floor((now.getTime() - updateTime.getTime()) / (1000 * 60));
          
          if (minutesAgo < 5) {
            console.log(`Data is fresh (updated ${minutesAgo} minutes ago)`);
          } else {
            console.log(`Data is ${minutesAgo} minutes old. Backend may be sleeping.`);
          }
        }
        
        console.log(`Successfully loaded ${firebaseData.length} students from Firebase`);
      } else {
        throw new Error('No data available in Firebase');
      }
    } catch (error) {
      console.error('Failed to load from Firebase:', error);
      toast({
        title: "Error",
        description: "Unable to load data from Firebase. Please ensure backend has populated data at least once.",
        variant: "destructive",
      });
      setStudents([]);
      setDataSource(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Group students by department
  const studentsByDepartment = useMemo(() => {
    const grouped: Record<string, Student[]> = {};
    
    students.forEach(student => {
      let dept = student.department || student.course || 'Unknown';
      
      // Normalize department names
      if (dept.includes('BBA') || dept.includes('B.B.A')) dept = 'BBA';
      else if (dept.includes('Agriculture')) dept = 'BSc Agriculture';
      else if (dept.includes('BSc') || dept.includes('B.Sc')) dept = 'BSc';
      else if (dept.includes('BTech') || dept.includes('B.Tech')) dept = 'BTech';
      
      if (!grouped[dept]) {
        grouped[dept] = [];
      }
      grouped[dept].push(student);
    });
    
    return grouped;
  }, [students]);

  // Get sorted departments (BBA, BSc, BSc Agriculture, BTech)
  const sortedDepartments = useMemo(() => {
    const order = ['BBA', 'BSc', 'BSc Agriculture', 'BTech'];
    return order.filter(dept => studentsByDepartment[dept]?.length > 0);
  }, [studentsByDepartment]);

  // Calculate overall stats
  const overallStats = useMemo(() => {
    return {
      total: students.length,
      red: students.filter(s => (s.final_phase || s.phase) === 'Red').length,
      orange: students.filter(s => (s.final_phase || s.phase) === 'Orange').length,
      yellow: students.filter(s => (s.final_phase || s.phase) === 'Yellow').length,
      green: students.filter(s => (s.final_phase || s.phase) === 'Green').length,
    };
  }, [students]);

  const handleStudentClick = (enrollmentNo: string) => {
    navigate(`/student/${enrollmentNo}`);
  };

  const bgStyle: React.CSSProperties = {
    background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                 radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                 linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
  };

  if (isLoading) {
    return (
      <motion.div 
        className="min-h-screen text-white" 
        style={bgStyle}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <SiteHeader />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <Skeleton variant="text" className="h-8 w-64 mb-2 bg-white/20" />
            <Skeleton variant="text" className="h-5 w-96 bg-white/10" />
          </div>

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
        </div>
      </motion.div>
    );
  }

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
        {/* Data Source Indicator */}
        {dataSource === 'firebase' && students.length > 0 && (
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-3 flex items-center gap-3"
          >
            <Database className="w-5 h-5 text-blue-400" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-100">
                Real-time Firebase Data
              </p>
              <p className="text-xs text-blue-200/80">
                {(() => {
                  const firstStudent = students[0] as any;
                  if (firstStudent?.lastUpdated) {
                    const updateTime = new Date(firstStudent.lastUpdated);
                    const now = new Date();
                    const minutesAgo = Math.floor((now.getTime() - updateTime.getTime()) / (1000 * 60));
                    
                    if (minutesAgo < 1) {
                      return "Just updated • Backend is active";
                    } else if (minutesAgo < 60) {
                      return `Last updated ${minutesAgo} minute${minutesAgo === 1 ? '' : 's'} ago`;
                    } else {
                      const hoursAgo = Math.floor(minutesAgo / 60);
                      return `Last updated ${hoursAgo} hour${hoursAgo === 1 ? '' : 's'} ago • Backend may be sleeping`;
                    }
                  }
                  return "Data loaded from Firebase";
                })()}
              </p>
            </div>
          </motion.div>
        )}

        {/* Header */}
        <motion.div 
          className="flex flex-col md:flex-row md:items-center justify-between gap-4"
          initial={{ y: -30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div>
            <h1 className="text-3xl font-bold [text-shadow:_0_3px_0_rgba(0,0,0,.25)]">
              Student Guardian Dashboard
            </h1>
            <p className="text-white/90 mt-2">
              Monitoring {students.length} students across {sortedDepartments.length} departments
            </p>
          </div>

          {/* Quick Stats */}
          <div className="flex gap-2 flex-wrap">
            <Badge variant="destructive" className="text-sm px-3 py-1">
              {overallStats.red} Critical
            </Badge>
            <Badge className="text-sm px-3 py-1 bg-orange-500 hover:bg-orange-600">
              {overallStats.orange} At Risk
            </Badge>
            <Badge className="text-sm px-3 py-1 bg-yellow-500 hover:bg-yellow-600">
              {overallStats.yellow} Monitor
            </Badge>
            <Badge className="text-sm px-3 py-1 bg-green-500 hover:bg-green-600">
              {overallStats.green} Safe
            </Badge>
          </div>
        </motion.div>

        {/* View Mode Toggle and Controls */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="bg-white/95 backdrop-blur border-0">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
                {/* View Mode Tabs */}
                <div className="flex gap-2">
                  <Button
                    variant={viewMode === 'analytics' ? 'default' : 'outline'}
                    onClick={() => setViewMode('analytics')}
                    className="gap-2"
                  >
                    <TrendingUp className="w-4 h-4" />
                    Analytics
                  </Button>
                  <Button
                    variant={viewMode === 'departments' ? 'default' : 'outline'}
                    onClick={() => setViewMode('departments')}
                    className="gap-2"
                  >
                    <AlertTriangle className="w-4 h-4" />
                    Departments
                  </Button>
                </div>

                {/* Search and Filters */}
                <div className="flex gap-2 w-full md:w-auto">
                  <div className="relative flex-1 md:w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search students..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setShowFilters(!showFilters)}
                    className={showFilters ? 'bg-primary text-white' : ''}
                  >
                    <Filter className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Filter Options */}
              {showFilters && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4"
                >
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-1 block">
                      Risk Phase
                    </label>
                    <Select value={filterPhase} onValueChange={setFilterPhase}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Phases" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All Phases</SelectItem>
                        <SelectItem value="Red">Red (Critical)</SelectItem>
                        <SelectItem value="Orange">Orange (At Risk)</SelectItem>
                        <SelectItem value="Yellow">Yellow (Monitor)</SelectItem>
                        <SelectItem value="Green">Green (Safe)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-1 block">
                      Gender
                    </label>
                    <Select value={filterGender} onValueChange={setFilterGender}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Genders" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All Genders</SelectItem>
                        <SelectItem value="Male">Male</SelectItem>
                        <SelectItem value="Female">Female</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-end">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setFilterPhase('');
                        setFilterGender('');
                        setSearchTerm('');
                      }}
                      className="w-full"
                    >
                      Clear Filters
                    </Button>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Content Area */}
        {viewMode === 'analytics' ? (
          <AnalyticsOverview students={students} />
        ) : (
          <div className="space-y-6">
            {sortedDepartments.map((department, index) => (
              <motion.div
                key={department}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * index }}
              >
                <DepartmentSection
                  department={department}
                  students={studentsByDepartment[department]}
                  searchTerm={searchTerm}
                  filterPhase={filterPhase}
                  filterGender={filterGender}
                  accentColor={DEPARTMENT_COLORS[department] || '#6366f1'}
                  onStudentClick={handleStudentClick}
                />
              </motion.div>
            ))}

            {sortedDepartments.length === 0 && (
              <Card className="bg-white/95 backdrop-blur border-0">
                <CardContent className="p-12 text-center">
                  <p className="text-gray-500">No students found matching your criteria.</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Quick Actions */}
        <motion.div
          className="flex justify-center pt-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Button 
            onClick={() => navigate('/simulation')}
            className="bg-gradient-secondary hover:opacity-90 gap-2"
            size="lg"
          >
            <TrendingUp className="w-5 h-5" />
            Run Student Simulation
          </Button>
        </motion.div>
      </main>
    </motion.div>
  );
};

export default DashboardNew;
