import React from 'react';
import { motion } from 'framer-motion';
import { cn } from "../../lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: 'default' | 'card' | 'text' | 'avatar' | 'button';
  lines?: number;
  animate?: boolean;
}

function Skeleton({ 
  className, 
  variant = 'default', 
  lines = 1,
  animate = true
}: SkeletonProps) {
  const baseClasses = "bg-gray-200 rounded-md shimmer";

  const variants = {
    default: "h-4 w-full",
    card: "h-32 w-full",
    text: "h-4",
    avatar: "h-12 w-12 rounded-full",
    button: "h-10 w-24 rounded-lg"
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <motion.div
            key={index}
            className={cn(
              baseClasses,
              variants.text,
              index === lines - 1 ? "w-3/4" : "w-full",
              className
            )}
            initial={animate ? { opacity: 0 } : undefined}
            animate={animate ? { opacity: 1 } : undefined}
            transition={animate ? { duration: 0.3, delay: index * 0.1 } : undefined}
          />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      className={cn(
        baseClasses,
        variants[variant],
        className
      )}
      initial={animate ? { opacity: 0 } : undefined}
      animate={animate ? { opacity: 1 } : undefined}
      transition={animate ? { duration: 0.3 } : undefined}
    />
  );
}

// Pre-built skeleton components for common use cases
export const TableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({ 
  rows = 5, 
  cols = 4 
}) => (
  <div className="space-y-4">
    <div className="grid grid-cols-4 gap-4">
      {Array.from({ length: cols }).map((_, colIndex) => (
        <Skeleton key={colIndex} variant="text" className="h-6 font-medium" />
      ))}
    </div>
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="grid grid-cols-4 gap-4">
        {Array.from({ length: cols }).map((_, colIndex) => (
          <Skeleton key={colIndex} variant="text" />
        ))}
      </div>
    ))}
  </div>
);

export const CardSkeleton: React.FC = () => (
  <div className="border rounded-lg p-6 space-y-4">
    <div className="flex items-center space-x-4">
      <Skeleton variant="avatar" />
      <div className="space-y-2 flex-1">
        <Skeleton variant="text" className="w-1/2" />
        <Skeleton variant="text" className="w-1/3" />
      </div>
    </div>
    <Skeleton variant="text" lines={3} />
    <div className="flex space-x-2">
      <Skeleton variant="button" />
      <Skeleton variant="button" />
    </div>
  </div>
);

export const StatCardSkeleton: React.FC = () => (
  <div className="border rounded-lg p-6">
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <Skeleton variant="text" className="w-24" />
        <Skeleton variant="text" className="w-16 h-8" />
      </div>
      <Skeleton variant="avatar" className="w-12 h-12" />
    </div>
  </div>
);

export { Skeleton };

