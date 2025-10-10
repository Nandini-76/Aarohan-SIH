import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Users, TrendingUp, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Student } from '../types';
import { cn } from '../lib/utils';
import StudentCard from './StudentCard';

interface DepartmentSectionProps {
  department: string;
  students: Student[];
  searchTerm: string;
  filterPhase: string;
  filterGender: string;
  accentColor: string;
  onStudentClick: (enrollmentNo: string) => void;
}

const DepartmentSection: React.FC<DepartmentSectionProps> = ({
  department,
  students,
  searchTerm,
  filterPhase,
  filterGender,
  accentColor,
  onStudentClick,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [expandedYears, setExpandedYears] = useState<Set<number>>(new Set([1, 2, 3, 4]));

  // Group students by year
  const studentsByYear = useMemo(() => {
    const grouped: Record<number, Student[]> = {};
    
    students.forEach(student => {
      const year = student.year_level || 1;
      if (!grouped[year]) {
        grouped[year] = [];
      }
      grouped[year].push(student);
    });

    // Sort students within each year by risk (Red > Orange > Yellow > Green)
    const riskPriority = { Red: 1, Orange: 2, Yellow: 3, Green: 4 };
    Object.keys(grouped).forEach(year => {
      grouped[Number(year)] = grouped[Number(year)].sort((a, b) => {
        const phaseA = a.final_phase || a.phase || 'Green';
        const phaseB = b.final_phase || b.phase || 'Green';
        const priorityA = riskPriority[phaseA as keyof typeof riskPriority] || 5;
        const priorityB = riskPriority[phaseB as keyof typeof riskPriority] || 5;
        if (priorityA !== priorityB) {
          return priorityA - priorityB;
        }
        return a.enrollment_no.localeCompare(b.enrollment_no);
      });
    });

    return grouped;
  }, [students]);

  // Apply filters
  const getFilteredStudents = (yearStudents: Student[]) => {
    return yearStudents.filter(student => {
      const matchesSearch = !searchTerm || 
        student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.enrollment_no.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesPhase = !filterPhase || filterPhase === 'all' || (student.final_phase || student.phase) === filterPhase;
      const matchesGender = !filterGender || filterGender === 'all' || student.gender === filterGender;

      return matchesSearch && matchesPhase && matchesGender;
    });
  };

  // Calculate stats for a year
  const calculateYearStats = (yearStudents: Student[]) => {
    const filtered = getFilteredStudents(yearStudents);
    const avgPhase = filtered.reduce((sum, s) => {
      const phaseValue = { Green: 4, Yellow: 3, Orange: 2, Red: 1 }[(s.final_phase || s.phase) as string] || 4;
      return sum + phaseValue;
    }, 0) / (filtered.length || 1);

    return {
      total: filtered.length,
      red: filtered.filter(s => (s.final_phase || s.phase) === 'Red').length,
      orange: filtered.filter(s => (s.final_phase || s.phase) === 'Orange').length,
      yellow: filtered.filter(s => (s.final_phase || s.phase) === 'Yellow').length,
      green: filtered.filter(s => (s.final_phase || s.phase) === 'Green').length,
      avgCGPA: (filtered.reduce((sum, s) => sum + s.cgpa, 0) / (filtered.length || 1)).toFixed(2),
      avgAttendance: (filtered.reduce((sum, s) => sum + s.attendance, 0) / (filtered.length || 1)).toFixed(1),
    };
  };

  const toggleYear = (year: number) => {
    setExpandedYears(prev => {
      const newSet = new Set(prev);
      if (newSet.has(year)) {
        newSet.delete(year);
      } else {
        newSet.add(year);
      }
      return newSet;
    });
  };

  const totalStudents = Object.values(studentsByYear).reduce((sum, yearStudents) => {
    return sum + getFilteredStudents(yearStudents).length;
  }, 0);

  if (totalStudents === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="bg-white/95 backdrop-blur border-0 shadow-lg overflow-hidden">
        {/* Department Header */}
        <CardHeader
          className={cn(
            "cursor-pointer transition-all duration-200 hover:bg-opacity-80",
            `bg-gradient-to-r from-${accentColor}-100 to-${accentColor}-50 border-l-4`
          )}
          style={{
            borderLeftColor: accentColor,
            background: `linear-gradient(to right, ${accentColor}20, ${accentColor}10)`
          }}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isExpanded ? (
                <ChevronDown className="w-5 h-5 text-gray-700" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-700" />
              )}
              <CardTitle className="text-xl font-bold text-gray-800">{department}</CardTitle>
              <Badge variant="secondary" className="ml-2">
                {totalStudents} students
              </Badge>
            </div>
          </div>
        </CardHeader>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <CardContent className="p-5 space-y-5">
                {Object.entries(studentsByYear)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([year, yearStudents]) => {
                    const filteredStudents = getFilteredStudents(yearStudents);
                    if (filteredStudents.length === 0) return null;

                    const stats = calculateYearStats(yearStudents);
                    const isYearExpanded = expandedYears.has(Number(year));

                    return (
                      <div key={year} className="border rounded-lg overflow-hidden shadow-sm">
                        {/* Year Header */}
                        <div
                          className="bg-gray-50 p-4 cursor-pointer hover:bg-gray-100 transition-colors"
                          onClick={() => toggleYear(Number(year))}
                        >
                          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                            <div className="flex items-center gap-3">
                              {isYearExpanded ? (
                                <ChevronDown className="w-4 h-4 text-gray-600 flex-shrink-0" />
                              ) : (
                                <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />
                              )}
                              <h3 className="text-lg font-semibold text-gray-800">Year {year}</h3>
                              <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">{stats.total} students</Badge>
                            </div>

                            {/* Year Stats Summary */}
                            <div className="flex items-center gap-3 md:gap-4 text-sm flex-wrap ml-7 md:ml-0">
                              <div className="flex items-center gap-1.5">
                                <TrendingUp className="w-4 h-4 text-blue-600 flex-shrink-0" />
                                <span className="text-gray-700 font-medium">CGPA: {stats.avgCGPA}</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <Users className="w-4 h-4 text-purple-600 flex-shrink-0" />
                                <span className="text-gray-700 font-medium">Att: {stats.avgAttendance}%</span>
                              </div>
                              {(stats.red > 0 || stats.orange > 0) && (
                                <div className="flex items-center gap-1.5">
                                  <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                                  <span className="text-red-600 font-semibold">
                                    {stats.red + stats.orange} at risk
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Phase Distribution Bar */}
                          <div className="mt-3 flex gap-1 h-2 rounded-full overflow-hidden">
                            {stats.red > 0 && (
                              <div
                                className="bg-red-500"
                                style={{ width: `${(stats.red / stats.total) * 100}%` }}
                                title={`${stats.red} Red`}
                              />
                            )}
                            {stats.orange > 0 && (
                              <div
                                className="bg-orange-500"
                                style={{ width: `${(stats.orange / stats.total) * 100}%` }}
                                title={`${stats.orange} Orange`}
                              />
                            )}
                            {stats.yellow > 0 && (
                              <div
                                className="bg-yellow-500"
                                style={{ width: `${(stats.yellow / stats.total) * 100}%` }}
                                title={`${stats.yellow} Yellow`}
                              />
                            )}
                            {stats.green > 0 && (
                              <div
                                className="bg-green-500"
                                style={{ width: `${(stats.green / stats.total) * 100}%` }}
                                title={`${stats.green} Green`}
                              />
                            )}
                          </div>
                        </div>

                        {/* Year Content - Student Cards */}
                        <AnimatePresence>
                          {isYearExpanded && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.3 }}
                              className="p-4"
                            >
                              <StudentCardGrid
                                students={filteredStudents}
                                onStudentClick={onStudentClick}
                              />
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    );
                  })}
              </CardContent>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
};

// Student Card Grid Component with Pagination
interface StudentCardGridProps {
  students: Student[];
  onStudentClick: (enrollmentNo: string) => void;
  studentsPerPage?: number;
}

const StudentCardGrid: React.FC<StudentCardGridProps> = ({
  students,
  onStudentClick,
  studentsPerPage = 30,
}) => {
  const [visibleCount, setVisibleCount] = useState(studentsPerPage);

  const visibleStudents = students.slice(0, visibleCount);
  const hasMore = visibleCount < students.length;

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visibleStudents.map((student, index) => (
          <motion.div
            key={student.enrollment_no}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: Math.min(index * 0.02, 0.5) }}
          >
            <StudentCard student={student} onClick={() => onStudentClick(student.enrollment_no)} />
          </motion.div>
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-2">
          <Button
            variant="outline"
            onClick={() => setVisibleCount(prev => prev + studentsPerPage)}
            className="w-full sm:w-auto px-6 py-2 font-medium"
          >
            Load More ({students.length - visibleCount} remaining)
          </Button>
        </div>
      )}
    </div>
  );
};

export default DepartmentSection;
