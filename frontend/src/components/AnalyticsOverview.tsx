import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Users, GraduationCap, TrendingUp, Award } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, CartesianGrid, Legend } from 'recharts';
import { Student } from '../types';
import { cn } from '../lib/utils';

interface AnalyticsOverviewProps {
  students: Student[];
}

const DEPARTMENT_COLORS = {
  'BBA': '#3b82f6',
  'BSc': '#8b5cf6',
  'BSc Agriculture': '#10b981',
  'BTech': '#f59e0b',
};

const PHASE_COLORS = {
  'Green': '#22c55e',
  'Yellow': '#eab308',
  'Orange': '#fb923c',
  'Red': '#ef4444',
};

const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({ students }) => {
  const analytics = useMemo(() => {
    // Department distribution
    const deptCounts: Record<string, number> = {};
    students.forEach(s => {
      const dept = s.department || 'Unknown';
      deptCounts[dept] = (deptCounts[dept] || 0) + 1;
    });

    // Year-wise distribution
    const yearCounts: Record<number, number> = {};
    students.forEach(s => {
      const year = s.year_level || 1;
      yearCounts[year] = (yearCounts[year] || 0) + 1;
    });

    // Average performance by department
    const deptStats: Record<string, { total: number; avgCGPA: number; avgAttendance: number; avgPhase: number }> = {};
    students.forEach(s => {
      const dept = s.department || 'Unknown';
      if (!deptStats[dept]) {
        deptStats[dept] = { total: 0, avgCGPA: 0, avgAttendance: 0, avgPhase: 0 };
      }
      deptStats[dept].total += 1;
      deptStats[dept].avgCGPA += s.cgpa;
      deptStats[dept].avgAttendance += s.attendance;
      
      // Convert phase to numeric for averaging (Green=4, Yellow=3, Orange=2, Red=1)
      const phaseValue = { Green: 4, Yellow: 3, Orange: 2, Red: 1 }[s.final_phase || s.phase || 'Green'];
      deptStats[dept].avgPhase += phaseValue;
    });

    // Calculate averages
    Object.keys(deptStats).forEach(dept => {
      const count = deptStats[dept].total;
      deptStats[dept].avgCGPA = Number((deptStats[dept].avgCGPA / count).toFixed(2));
      deptStats[dept].avgAttendance = Number((deptStats[dept].avgAttendance / count).toFixed(1));
      deptStats[dept].avgPhase = Number((deptStats[dept].avgPhase / count).toFixed(2));
    });

    // Phase distribution
    const phaseCounts = {
      Green: students.filter(s => (s.final_phase || s.phase) === 'Green').length,
      Yellow: students.filter(s => (s.final_phase || s.phase) === 'Yellow').length,
      Orange: students.filter(s => (s.final_phase || s.phase) === 'Orange').length,
      Red: students.filter(s => (s.final_phase || s.phase) === 'Red').length,
    };

    return {
      totalStudents: students.length,
      deptCounts,
      yearCounts,
      deptStats,
      phaseCounts,
      avgCGPA: Number((students.reduce((sum, s) => sum + s.cgpa, 0) / students.length).toFixed(2)),
      avgAttendance: Number((students.reduce((sum, s) => sum + s.attendance, 0) / students.length).toFixed(1)),
    };
  }, [students]);

  // Prepare chart data
  const deptChartData = Object.entries(analytics.deptCounts).map(([dept, count]) => ({
    department: dept,
    students: count,
    avgCGPA: analytics.deptStats[dept]?.avgCGPA || 0,
    avgAttendance: analytics.deptStats[dept]?.avgAttendance || 0,
  }));

  const yearChartData = Object.entries(analytics.yearCounts)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([year, count]) => ({
      year: `Year ${year}`,
      students: count,
    }));

  const phaseChartData = Object.entries(analytics.phaseCounts).map(([phase, count]) => ({
    name: phase,
    value: count,
    color: PHASE_COLORS[phase as keyof typeof PHASE_COLORS],
  }));

  const statCards = [
    {
      title: "Total Students",
      value: analytics.totalStudents,
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
    },
    {
      title: "Departments",
      value: Object.keys(analytics.deptCounts).length,
      icon: GraduationCap,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      borderColor: "border-purple-200",
    },
    {
      title: "Average CGPA",
      value: analytics.avgCGPA,
      icon: Award,
      color: "text-emerald-600",
      bgColor: "bg-emerald-50",
      borderColor: "border-emerald-200",
    },
    {
      title: "Average Attendance",
      value: `${analytics.avgAttendance}%`,
      icon: TrendingUp,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-200",
    },
  ];

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Analytics Overview</h2>
        <p className="text-white/80">Comprehensive insights into student performance and distribution</p>
      </div>

      {/* Summary Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <Card className={cn(
              "border-2 transition-all duration-300",
              stat.bgColor,
              stat.borderColor,
              "hover:shadow-lg"
            )}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <p className={cn("text-3xl font-bold", stat.color)}>{stat.value}</p>
                  </div>
                  <div className={cn("p-3 rounded-full", stat.bgColor)}>
                    <stat.icon className={cn("h-6 w-6", stat.color)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Distribution */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="bg-white/95 backdrop-blur border-0 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-gray-800">Student Distribution by Department</CardTitle>
            </CardHeader>
            <CardContent className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptChartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="department" 
                    tick={{ fontSize: 11 }} 
                    angle={-15}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                  />
                  <Bar dataKey="students" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Year-wise Distribution */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="bg-white/95 backdrop-blur border-0 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-gray-800">Year-wise Student Count</CardTitle>
            </CardHeader>
            <CardContent className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={yearChartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                  />
                  <Bar dataKey="students" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Performance by Department */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card className="bg-white/95 backdrop-blur border-0 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-gray-800">Average Performance by Department</CardTitle>
            </CardHeader>
            <CardContent className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptChartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="department" 
                    tick={{ fontSize: 11 }} 
                    angle={-15}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                  />
                  <Legend />
                  <Bar dataKey="avgCGPA" fill="#10b981" radius={[4, 4, 0, 0]} name="Avg CGPA" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Phase Distribution Pie Chart */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Card className="bg-white/95 backdrop-blur border-0 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-gray-800">Risk Phase Distribution</CardTitle>
            </CardHeader>
            <CardContent className="h-80 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={phaseChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                  >
                    {phaseChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default AnalyticsOverview;
