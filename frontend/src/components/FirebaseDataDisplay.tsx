/**
 * Firebase Data Display Component
 * 
 * Example component showing how to use Firebase in your React application.
 * This component listens to real-time updates from Firebase and displays
 * the latest prediction data, even when the backend is sleeping.
 */

import { useEffect, useState } from 'react';
import { listenToLatestData, getFirebaseStatus } from '@/services/firebase';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Activity, AlertCircle } from 'lucide-react';

interface LatestSimulation {
  enrollment_no: string;
  final_phase: string;
  risk_level: string;
  ml_probability: number;
  rule_override: boolean;
}

interface FirebaseData {
  timestamp: string;
  latest_simulation?: LatestSimulation;
  backend_status: string;
  lastUpdated: string;
}

export const FirebaseDataDisplay = () => {
  const [data, setData] = useState<FirebaseData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check Firebase status
    const status = getFirebaseStatus();
    setIsConnected(status.initialized);

    if (!status.initialized) {
      setIsLoading(false);
      return;
    }

    // Set up real-time listener
    const unsubscribe = listenToLatestData((firebaseData) => {
      if (firebaseData) {
        setData(firebaseData);
      }
      setIsLoading(false);
    });

    // Cleanup listener on unmount
    return () => {
      unsubscribe();
    };
  }, []);

  // Get risk color based on phase
  const getRiskColor = (phase: string) => {
    switch (phase) {
      case 'Red':
        return 'destructive';
      case 'Orange':
        return 'default'; // You can create a custom orange variant
      case 'Yellow':
        return 'secondary';
      case 'Green':
        return 'outline';
      default:
        return 'default';
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 animate-spin" />
            Loading Firebase Data...
          </CardTitle>
        </CardHeader>
      </Card>
    );
  }

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-yellow-600">
            <AlertCircle className="h-5 w-5" />
            Firebase Not Configured
          </CardTitle>
          <CardDescription>
            Firebase environment variables are not set. Configure them in Vercel to enable real-time data sync.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Data Available</CardTitle>
          <CardDescription>
            Waiting for first simulation to run...
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Latest Prediction Results</span>
          <Badge variant={data.backend_status === 'active' ? 'default' : 'secondary'}>
            {data.backend_status === 'active' ? 'Backend Active' : 'Backend Sleeping'}
          </Badge>
        </CardTitle>
        <CardDescription className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Last Updated: {formatTimestamp(data.lastUpdated)}
        </CardDescription>
      </CardHeader>
      
      {data.latest_simulation && (
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Student ID</p>
                <p className="text-lg font-semibold">{data.latest_simulation.enrollment_no}</p>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground">Risk Level</p>
                <Badge variant={getRiskColor(data.latest_simulation.final_phase)}>
                  {data.latest_simulation.risk_level}
                </Badge>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground">Phase</p>
                <p className="text-lg font-semibold">{data.latest_simulation.final_phase}</p>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground">ML Probability</p>
                <p className="text-lg font-semibold">
                  {(data.latest_simulation.ml_probability * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            
            {data.latest_simulation.rule_override && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-sm text-yellow-800">
                  ⚠️ Risk level was overridden by rule-based system
                </p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default FirebaseDataDisplay;
