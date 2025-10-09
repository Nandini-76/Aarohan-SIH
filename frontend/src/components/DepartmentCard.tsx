import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Users, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface DepartmentCardProps {
  id: string;
  name: string;
  studentCount: number;
  riskDistribution: {
    critical: number;
    atRisk: number;
    monitor: number;
    safe: number;
  };
  avgCgpa: number;
  avgAttendance: number;
  performanceScore: number;
  color?: string;
}

const DEPARTMENT_COLORS: Record<string, string> = {
  bba: '#3b82f6',
  bsc: '#8b5cf6',
  'bsc_agriculture': '#10b981',
  btech: '#f59e0b',
};

export const DepartmentCard: React.FC<DepartmentCardProps> = ({
  id,
  name,
  studentCount,
  riskDistribution,
  avgCgpa,
  avgAttendance,
  performanceScore,
  color,
}) => {
  const deptColor = color || DEPARTMENT_COLORS[id.toLowerCase()] || '#6b7280';
  
  return (
    <Link to={`/department/${id}`} className="block">
      <motion.div
        whileHover={{ scale: 1.02, y: -4 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.2 }}
      >
        <Card 
          className="cursor-pointer shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border-2 hover:border-primary/50"
          style={{ borderTopColor: deptColor, borderTopWidth: '4px' }}
        >
          <CardContent className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold" style={{ color: deptColor }}>
                  {name}
                </h2>
                <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                  <Users className="h-4 w-4" />
                  <span>{studentCount} students</span>
                </div>
              </div>
              <div 
                className="h-16 w-16 rounded-full flex items-center justify-center text-white font-bold text-lg"
                style={{ backgroundColor: deptColor }}
              >
                {name.charAt(0)}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-secondary/20 rounded-lg p-3">
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                  <TrendingUp className="h-3 w-3" />
                  <span>Avg CGPA</span>
                </div>
                <div className="text-2xl font-bold">{avgCgpa.toFixed(1)}</div>
              </div>
              <div className="bg-secondary/20 rounded-lg p-3">
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>Attendance</span>
                </div>
                <div className="text-2xl font-bold">{avgAttendance.toFixed(0)}%</div>
              </div>
            </div>

            {/* Risk Summary */}
            <div className="space-y-2 mb-4">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <AlertTriangle className="h-4 w-4" />
                <span>Risk Distribution</span>
              </div>
              <div className="flex gap-2 flex-wrap">
                <Badge 
                  variant="destructive" 
                  className="px-2 py-1"
                >
                  {riskDistribution.critical} Critical
                </Badge>
                <Badge 
                  variant="default" 
                  className="px-2 py-1 bg-orange-500 hover:bg-orange-600"
                >
                  {riskDistribution.atRisk} At Risk
                </Badge>
                <Badge 
                  variant="default" 
                  className="px-2 py-1 bg-yellow-500 hover:bg-yellow-600 text-black"
                >
                  {riskDistribution.monitor} Monitor
                </Badge>
                <Badge 
                  variant="default" 
                  className="px-2 py-1 bg-green-500 hover:bg-green-600"
                >
                  {riskDistribution.safe} Safe
                </Badge>
              </div>
            </div>

            {/* Performance Score */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Performance</span>
                <span className="font-semibold">{performanceScore.toFixed(0)}%</span>
              </div>
              <Progress 
                value={performanceScore} 
                className="h-2"
                style={{
                  //@ts-ignore
                  '--progress-background': deptColor,
                }}
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </Link>
  );
};

export default DepartmentCard;
