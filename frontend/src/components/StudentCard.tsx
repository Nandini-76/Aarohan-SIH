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
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={cn(
          "cursor-pointer transition-all duration-200 border-2 overflow-hidden h-full",
          borderColorClass,
          glowClass,
          "hover:shadow-xl bg-white"
        )}
        onClick={onClick}
      >
        <CardContent className="p-4 space-y-3">
          {/* Header - Student Info */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2.5 flex-1 min-w-0">
              <div className="bg-gradient-to-br from-gray-100 to-gray-200 rounded-full p-2.5 flex-shrink-0">
                <User className="w-4 h-4 text-gray-700" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="font-semibold text-gray-900 truncate text-sm leading-tight" title={student.name}>
                  {student.name || 'Unknown'}
                </h3>
                <p className="text-xs text-gray-500 truncate mt-0.5" title={student.enrollment_no}>
                  {student.enrollment_no}
                </p>
              </div>
            </div>
            <RiskBadge 
              phase={phase} 
              showIcon={phase === 'Red' || phase === 'Orange'}
              className="flex-shrink-0 ml-1"
            />
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-2.5 pt-2.5 border-t border-gray-100">
            {/* CGPA */}
            <div className="flex items-center gap-1.5">
              <div className="bg-blue-50 rounded p-1.5 flex-shrink-0">
                <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
              </div>
              <div className="min-w-0">
                <p className="text-[10px] text-gray-500 uppercase tracking-wide">CGPA</p>
                <p className={cn(
                  "text-sm font-bold leading-tight",
                  student.cgpa >= 8 ? "text-green-600" :
                  student.cgpa >= 6 ? "text-yellow-600" : "text-red-600"
                )}>
                  {student.cgpa.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Attendance */}
            <div className="flex items-center gap-1.5">
              <div className="bg-purple-50 rounded p-1.5 flex-shrink-0">
                <BookOpen className="w-3.5 h-3.5 text-purple-600" />
              </div>
              <div className="min-w-0">
                <p className="text-[10px] text-gray-500 uppercase tracking-wide">Attendance</p>
                <p className={cn(
                  "text-sm font-bold leading-tight",
                  student.attendance >= 75 ? "text-green-600" :
                  student.attendance >= 60 ? "text-yellow-600" : "text-red-600"
                )}>
                  {student.attendance}%
                </p>
              </div>
            </div>

            {/* Backlogs */}
            {student.backlogs > 0 && (
              <div className="col-span-2 flex items-center gap-2 bg-orange-50 rounded-md px-2.5 py-2 mt-1">
                <AlertCircle className="w-4 h-4 text-orange-600 flex-shrink-0" />
                <p className="text-xs text-orange-800 font-semibold">
                  {student.backlogs} Backlog{student.backlogs > 1 ? 's' : ''}
                </p>
              </div>
            )}
          </div>

          {/* Risk Reason (if any) */}
          {(student.override_reason || student.risk_reason) && (
            <div className="pt-2.5 border-t border-gray-100">
              <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed" title={student.override_reason || student.risk_reason}>
                {student.override_reason || student.risk_reason}
              </p>
            </div>
          )}

          {/* Additional Info Tags */}
          {(student.gender || student.fees_flag === 1 || student.suspension_flag === 1) && (
            <div className="flex flex-wrap gap-1.5 pt-2">
              {student.gender && (
                <Badge variant="outline" className="text-xs px-2 py-0.5 font-medium">
                  {student.gender}
                </Badge>
              )}
              {student.fees_flag === 1 && (
                <Badge variant="destructive" className="text-xs px-2 py-0.5 font-medium">
                  Fees Pending
                </Badge>
              )}
              {student.suspension_flag === 1 && (
                <Badge variant="destructive" className="text-xs px-2 py-0.5 font-medium">
                  Suspended
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default StudentCard;
