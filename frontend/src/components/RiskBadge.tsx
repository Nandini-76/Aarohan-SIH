import React from 'react';
import { cn } from '../lib/utils';
import { Badge } from './ui/badge';
import { AlertTriangle } from 'lucide-react';

interface RiskBadgeProps {
  phase: "Green" | "Yellow" | "Orange" | "Red";
  className?: string;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ 
  phase, 
  className, 
  showIcon = false,
  size = 'md'
}) => {
  const getBadgeStyles = (phase: string) => {
    switch (phase) {
      case "Green":
        return "bg-success text-success-foreground";
      case "Yellow":
        return "bg-warning text-warning-foreground";
      case "Orange":
        return "bg-orange text-orange-foreground";
      case "Red":
        return "bg-destructive text-destructive-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getSizeStyles = (size: string) => {
    switch (size) {
      case "sm":
        return "px-2 py-0.5 text-xs";
      case "lg":
        return "px-4 py-2 text-base";
      default:
        return "px-2.5 py-0.5 text-xs";
    }
  };

  const getRiskIcon = (phase: string) => {
    if (!showIcon) return null;
    
    switch (phase) {
      case "Red":
      case "Orange":
        return <AlertTriangle className="w-3 h-3 mr-1" />;
      default:
        return null;
    }
  };
  return (
    <span 
      className={cn(
        "inline-flex items-center rounded-full font-medium transition-all duration-200",
        getBadgeStyles(phase),
        getSizeStyles(size),
        className
      )}
    >
      {getRiskIcon(phase)}
      {phase}
    </span>
  );
};

export default RiskBadge;