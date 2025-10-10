import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Filter, Download, Users } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { useToast } from '../hooks/use-toast';

interface Student {
  enrollmentNo: string;
  name: string;
  department: string;
  year: number;
  section: string;
  cgpa: number;
  attendance: number;
  backlogs: number;
  riskPhase: string;
  status: string;
}

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
  initialSearchTerm?: string;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({
  isOpen,
  onClose,
  initialSearchTerm = '',
}) => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [searchTerm, setSearchTerm] = useState(initialSearchTerm);
  const [students, setStudents] = useState<Student[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [filterYear, setFilterYear] = useState('all');
  const [filterSection, setFilterSection] = useState('all');
  const [filterRisk, setFilterRisk] = useState('all');

  useEffect(() => {
    if (isOpen && searchTerm.length >= 2) {
      searchStudents();
    }
  }, [isOpen, searchTerm]);

  useEffect(() => {
    applyFilters();
  }, [students, filterDepartment, filterYear, filterSection, filterRisk]);

  const searchStudents = async () => {
    if (searchTerm.length < 2) {
      toast({
        title: "Search Term Too Short",
        description: "Please enter at least 2 characters",
        variant: "default",
      });
      return;
    }

    setIsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(
        `${apiUrl}/api/students/search?query=${encodeURIComponent(searchTerm)}`
      );

      if (!response.ok) {
        throw new Error('Failed to search students');
      }

      const data = await response.json();
      setStudents(data.students || []);
    } catch (error) {
      console.error('Error searching students:', error);
      toast({
        title: "Search Failed",
        description: "Failed to search students. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...students];

    if (filterDepartment && filterDepartment !== 'all') {
      filtered = filtered.filter(s => s.department === filterDepartment);
    }

    if (filterYear && filterYear !== 'all') {
      filtered = filtered.filter(s => s.year === parseInt(filterYear));
    }

    if (filterSection && filterSection !== 'all') {
      filtered = filtered.filter(s => s.section === filterSection);
    }

    if (filterRisk && filterRisk !== 'all') {
      filtered = filtered.filter(s => s.riskPhase === filterRisk);
    }

    setFilteredStudents(filtered);
  };

  const clearFilters = () => {
    setFilterDepartment('all');
    setFilterYear('all');
    setFilterSection('all');
    setFilterRisk('all');
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

    const headers = ['Enrollment No', 'Name', 'Department', 'Year', 'Section', 'CGPA', 'Attendance', 'Backlogs', 'Risk Phase', 'Status'];
    const csvContent = [
      headers.join(','),
      ...filteredStudents.map(s =>
        [s.enrollmentNo, s.name, s.department, s.year, s.section, s.cgpa, s.attendance, s.backlogs, s.riskPhase, s.status].join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `search_results_${searchTerm}_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast({
      title: "Export Successful",
      description: `Exported ${filteredStudents.length} students to CSV`,
      variant: "default",
    });
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

  const uniqueDepartments = Array.from(new Set(students.map(s => s.department)));
  const uniqueYears = Array.from(new Set(students.map(s => s.year))).sort();
  const uniqueSections = Array.from(new Set(students.map(s => s.section))).sort();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Global Student Search
          </DialogTitle>
          <DialogDescription>
            Search for students by name or enrollment number
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Search Bar */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name or enrollment number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    searchStudents();
                  }
                }}
                className="pl-10"
                autoFocus
              />
            </div>
            <Button onClick={searchStudents} disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
          </div>

          {/* Results Summary */}
          {students.length > 0 && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    Found <strong>{students.length}</strong> students
                    {filteredStudents.length !== students.length && (
                      <span> • Showing <strong>{filteredStudents.length}</strong> filtered</span>
                    )}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                {(filterDepartment || filterYear || filterSection || filterRisk) && (
                  <Button variant="outline" size="sm" onClick={clearFilters}>
                    <X className="h-4 w-4 mr-2" />
                    Clear Filters
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={exportToCSV}>
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </div>
          )}

          {/* Filters */}
          {students.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Departments" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Departments</SelectItem>
                      {uniqueDepartments.map((dept) => (
                        <SelectItem key={dept} value={dept}>
                          {dept}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={filterYear} onValueChange={setFilterYear}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Years" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Years</SelectItem>
                      {uniqueYears.map((year) => (
                        <SelectItem key={year} value={year.toString()}>
                          Year {year}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={filterSection} onValueChange={setFilterSection}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Sections" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Sections</SelectItem>
                      {uniqueSections.map((section) => (
                        <SelectItem key={section} value={section}>
                          Section {section}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={filterRisk} onValueChange={setFilterRisk}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Risk Levels" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Risk Levels</SelectItem>
                      <SelectItem value="Red">Critical</SelectItem>
                      <SelectItem value="Orange">At Risk</SelectItem>
                      <SelectItem value="Yellow">Monitor</SelectItem>
                      <SelectItem value="Green">Safe</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Results Table */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-muted-foreground">Searching students...</p>
              </div>
            </div>
          ) : filteredStudents.length > 0 ? (
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold">Enrollment No</th>
                        <th className="text-left py-3 px-4 font-semibold">Name</th>
                        <th className="text-left py-3 px-4 font-semibold">Department</th>
                        <th className="text-left py-3 px-4 font-semibold">Year</th>
                        <th className="text-left py-3 px-4 font-semibold">Section</th>
                        <th className="text-left py-3 px-4 font-semibold">CGPA</th>
                        <th className="text-left py-3 px-4 font-semibold">Attendance</th>
                        <th className="text-left py-3 px-4 font-semibold">Risk</th>
                      </tr>
                    </thead>
                    <tbody>
                      <AnimatePresence>
                        {filteredStudents.map((student, index) => (
                          <motion.tr
                            key={student.enrollmentNo}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ delay: index * 0.02 }}
                            className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                            onClick={() => {
                              onClose();
                              navigate(`/student/${student.enrollmentNo}`);
                            }}
                          >
                            <td className="py-3 px-4 font-mono text-sm">{student.enrollmentNo}</td>
                            <td className="py-3 px-4 font-medium">{student.name}</td>
                            <td className="py-3 px-4">{student.department}</td>
                            <td className="py-3 px-4">Year {student.year}</td>
                            <td className="py-3 px-4">{student.section}</td>
                            <td className="py-3 px-4">
                              <span className="font-semibold">{student.cgpa.toFixed(2)}</span>
                            </td>
                            <td className="py-3 px-4">{student.attendance.toFixed(1)}%</td>
                            <td className="py-3 px-4">
                              <Badge variant={getRiskBadgeColor(student.riskPhase)}>
                                {student.riskPhase}
                              </Badge>
                            </td>
                          </motion.tr>
                        ))}
                      </AnimatePresence>
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ) : searchTerm.length >= 2 && !isLoading ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium">No students found</p>
              <p className="text-sm text-muted-foreground mt-2">
                Try adjusting your search term or filters
              </p>
            </div>
          ) : (
            <div className="text-center py-12">
              <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium">Start searching</p>
              <p className="text-sm text-muted-foreground mt-2">
                Enter at least 2 characters to search for students
              </p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default GlobalSearch;
