import React from 'react';
import { motion } from 'framer-motion';
import { User, TrendingUp, BookOpen, AlertCircle } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import RiskBadge from './RiskBadge';
import { Student } from '../types';
import { cn } from '../lib/utils';

interface StudentCardProps {
  student: Student;
  onClick: () => void;
}

const StudentCard: React.FC<StudentCardProps> = ({ student, onClick }) => {
  const phase = student.final_phase || student.phase || 'Green';
  
  // Card border color based on phase
  const borderColorClass = {
    Red: 'border-red-300 hover:border-red-400',
    Orange: 'border-orange-300 hover:border-orange-400',
    Yellow: 'border-yellow-300 hover:border-yellow-400',
    Green: 'border-green-300 hover:border-green-400',
  }[phase];

  // Background glow on hover
  const glowClass = {
    Red: 'hover:shadow-red-200/50',
    Orange: 'hover:shadow-orange-200/50',
    Yellow: 'hover:shadow-yellow-200/50',
    Green: 'hover:shadow-green-200/50',
  }[phase];

  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -4 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={cn(
          "cursor-pointer transition-all duration-200 border-2 overflow-hidden h-full",
          borderColorClass,
          glowClass,
          "hover:shadow-lg"
        )}
        onClick={onClick}
      >
        <CardContent className="p-4 space-y-3">
          {/* Header - Student Info */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <div className="bg-gray-100 rounded-full p-2 flex-shrink-0">
                <User className="w-5 h-5 text-gray-600" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="font-semibold text-gray-900 truncate" title={student.name}>
                  {student.name || 'Unknown'}
                </h3>
                <p className="text-xs text-gray-500 truncate" title={student.enrollment_no}>
                  {student.enrollment_no}
                </p>
              </div>
            </div>
            <RiskBadge 
              phase={phase} 
              showIcon={phase === 'Red' || phase === 'Orange'}
              className="flex-shrink-0"
            />
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
            {/* CGPA */}
            <div className="flex items-center gap-2">
              <div className="bg-blue-50 rounded p-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">CGPA</p>
                <p className={cn(
                  "text-sm font-semibold",
                  student.cgpa >= 8 ? "text-green-600" :
                  student.cgpa >= 6 ? "text-yellow-600" : "text-red-600"
                )}>
                  {student.cgpa.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Attendance */}
            <div className="flex items-center gap-2">
              <div className="bg-purple-50 rounded p-1.5">
                <BookOpen className="w-3.5 h-3.5 text-purple-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Attendance</p>
                <p className={cn(
                  "text-sm font-semibold",
                  student.attendance >= 75 ? "text-green-600" :
                  student.attendance >= 60 ? "text-yellow-600" : "text-red-600"
                )}>
                  {student.attendance}%
                </p>
              </div>
            </div>

            {/* Backlogs */}
            {student.backlogs > 0 && (
              <div className="col-span-2 flex items-center gap-2 bg-orange-50 rounded px-2 py-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-orange-600" />
                <div className="flex-1">
                  <p className="text-xs text-orange-800 font-medium">
                    {student.backlogs} Backlog{student.backlogs > 1 ? 's' : ''}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Risk Reason (if any) */}
          {(student.override_reason || student.risk_reason) && (
            <div className="pt-2 border-t border-gray-100">
              <p className="text-xs text-gray-600 line-clamp-2" title={student.override_reason || student.risk_reason}>
                {student.override_reason || student.risk_reason}
              </p>
            </div>
          )}

          {/* Additional Info Tags */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {student.gender && (
              <Badge variant="outline" className="text-xs px-2 py-0">
                {student.gender}
              </Badge>
            )}
            {student.fees_flag === 1 && (
              <Badge variant="destructive" className="text-xs px-2 py-0">
                Fees Pending
              </Badge>
            )}
            {student.suspension_flag === 1 && (
              <Badge variant="destructive" className="text-xs px-2 py-0">
                Suspended
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default StudentCard;
