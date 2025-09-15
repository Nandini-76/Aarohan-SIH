import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { ArrowLeft, Play, RefreshCw, Sliders, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Slider } from '../components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Separator } from '../components/ui/separator';
import { Progress } from '../components/ui/progress';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { studentApi } from '../services/api';
import { SimulationData, SimulationResult, Student } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '@/lib/utils';
import SiteHeader from '@/components/SiteHeader';

const Simulation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const studentFromProfile = location.state?.student as Student;

  const [formData, setFormData] = useState<SimulationData>({
    enrollment_no: studentFromProfile?.enrollment_no || '',
    attendance: studentFromProfile?.attendance || 75,
    cgpa: studentFromProfile?.cgpa || 7.0,
    backlogs: studentFromProfile?.backlogs || 0,
    marks_10th: studentFromProfile?.marks_10th || 75,
    marks_12th: studentFromProfile?.marks_12th || 75,
    fees_flag: studentFromProfile?.fees_flag ? 1 : 0,
    suspension_flag: studentFromProfile?.suspension_flag ? 1 : 0,
    gender: studentFromProfile?.gender || 'M',
  });

  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [realTimeMode, setRealTimeMode] = useState(false);

  // Real-time simulation when enabled
  useEffect(() => {
    if (realTimeMode && hasRun) {
      const timeoutId = setTimeout(() => {
        runSimulation(true); // Silent mode for real-time updates
      }, 500);
      
      return () => clearTimeout(timeoutId);
    }
  }, [formData, realTimeMode]);
  const handleInputChange = (field: keyof SimulationData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const runSimulation = async (silent = false) => {
    if (!silent) setIsLoading(true);
    
    try {
      const result = await studentApi.simulate(formData);
      setResult(result);
      setHasRun(true);

      if (!silent) {
        toast({
          title: "Simulation Complete",
          description: `Risk assessment: ${result.final_phase}`,
        });
      }
    } catch (error) {
      console.error('Simulation failed:', error);
      if (!silent) {
        toast({
          title: "Simulation Error",
          description: "Failed to run simulation. Please check if the backend server is running.",
          variant: "destructive",
        });
      }
    } finally {
      if (!silent) setIsLoading(false);
    }
  };

  const resetSimulation = () => {
    if (studentFromProfile) {
      setFormData({
        enrollment_no: studentFromProfile.enrollment_no,
        attendance: studentFromProfile.attendance,
        cgpa: studentFromProfile.cgpa,
        backlogs: studentFromProfile.backlogs,
        marks_10th: studentFromProfile.marks_10th,
        marks_12th: studentFromProfile.marks_12th,
        fees_flag: studentFromProfile.fees_flag,
        suspension_flag: studentFromProfile.suspension_flag,
        gender: studentFromProfile.gender,
      });
    } else {
      setFormData({
        enrollment_no: '',
        attendance: 75,
        cgpa: 7.0,
        backlogs: 0,
        marks_10th: 75,
        marks_12th: 75,
        fees_flag: 0,
        suspension_flag: 0,
        gender: 'M',
      });
    }
    setResult(null);
    setHasRun(false);
    setRealTimeMode(false);
  };

  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: '/simulation' }} />;

  const bgStyle: React.CSSProperties = {
    background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                 radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                 linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
  };

  return (
    <div className="min-h-screen text-white" style={bgStyle}>
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="p-2"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-2">
              <Sliders className="h-8 w-8 text-primary" />
              <span>Risk Simulation</span>
            </h1>
            <p className="text-white/90">
              Adjust parameters to predict student dropout risk
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Label htmlFor="realtime" className="text-sm">Real-time</Label>
          <Switch
            id="realtime"
            checked={realTimeMode}
            onCheckedChange={setRealTimeMode}
            disabled={!hasRun}
          />
        </div>
      </div>

      {studentFromProfile && (
        <Card className="border-primary bg-gradient-to-r from-primary/5 to-primary/10">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                <Info className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">Simulating for: {studentFromProfile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {studentFromProfile.enrollment_no} • {studentFromProfile.department}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Parameters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sliders className="h-5 w-5 text-primary" />
              <span>Simulation Parameters</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Enrollment Number (if not from profile) */}
            {!studentFromProfile && (
              <div className="space-y-2">
                <Label htmlFor="enrollment">Enrollment Number (Optional)</Label>
                <Input
                  id="enrollment"
                  type="text"
                  placeholder="e.g., 2023ENG001"
                  value={formData.enrollment_no || ''}
                  onChange={(e) => handleInputChange('enrollment_no', e.target.value)}
                />
              </div>
            )}

            {/* Attendance */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="attendance">Attendance (%)</Label>
                <span className="text-sm font-medium">{formData.attendance}%</span>
              </div>
              <Slider
                value={[formData.attendance]}
                onValueChange={(value) => handleInputChange('attendance', value[0])}
                max={100}
                min={0}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0%</span>
                <span className={formData.attendance < 70 ? "text-destructive font-medium" : ""}>
                  {formData.attendance < 70 ? "Below Minimum (70%)" : ""}
                </span>
                <span>100%</span>
              </div>
            </div>

            {/* CGPA */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="cgpa">CGPA</Label>
                <span className="text-sm font-medium">{formData.cgpa.toFixed(1)}</span>
              </div>
              <Slider
                value={[formData.cgpa]}
                onValueChange={(value) => handleInputChange('cgpa', value[0])}
                max={10}
                min={0}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0.0</span>
                <span className={formData.cgpa < 5 ? "text-destructive font-medium" : ""}>
                  {formData.cgpa < 5 ? "Below Average" : ""}
                </span>
                <span>10.0</span>
              </div>
            </div>

            {/* Backlogs */}
            <div className="space-y-2">
              <Label htmlFor="backlogs">Number of Backlogs</Label>
              <Input
                id="backlogs"
                type="number"
                min="0"
                max="15"
                value={formData.backlogs}
                onChange={(e) => handleInputChange('backlogs', Number(e.target.value))}
              />
              <p className={cn("text-xs", 
                formData.backlogs > 3 ? "text-destructive font-medium" : "text-muted-foreground"
              )}>
                {formData.backlogs > 3 ? "⚠️ High backlog count" : `Current: ${formData.backlogs}`}
              </p>
            </div>

            <Separator />

            {/* 10th Marks */}
            <div className="space-y-2">
              <Label htmlFor="marks-10th">10th Grade Marks (%)</Label>
              <Input
                id="marks-10th"
                type="number"
                min="0"
                max="100"
                value={formData.marks_10th}
                onChange={(e) => handleInputChange('marks_10th', Number(e.target.value))}
              />
            </div>

            {/* 12th Marks */}
            <div className="space-y-2">
              <Label htmlFor="marks-12th">12th Grade Marks (%)</Label>
              <Input
                id="marks-12th"
                type="number"
                min="0"
                max="100"
                value={formData.marks_12th}
                onChange={(e) => handleInputChange('marks_12th', Number(e.target.value))}
              />
            </div>

            {/* Gender */}
            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => handleInputChange('gender', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="M">Male</SelectItem>
                  <SelectItem value="F">Female</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Flags */}
            <div className="space-y-6">
              <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
                Risk Factors
              </h3>
              
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label htmlFor="fees-flag" className="font-medium">Outstanding Fees</Label>
                  <p className="text-xs text-muted-foreground">Student has unpaid fees</p>
                </div>
                <Switch
                  id="fees-flag"
                  checked={Boolean(formData.fees_flag)}
                  onCheckedChange={(checked) => handleInputChange('fees_flag', checked ? 1 : 0)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label htmlFor="suspension-flag" className="font-medium">Academic Suspension</Label>
                  <p className="text-xs text-muted-foreground">Student has disciplinary issues</p>
                </div>
                <Switch
                  id="suspension-flag"
                  checked={Boolean(formData.suspension_flag)}
                  onCheckedChange={(checked) => handleInputChange('suspension_flag', checked ? 1 : 0)}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-4">
              <Button
                onClick={() => runSimulation()}
                disabled={isLoading}
                className="flex-1 bg-gradient-primary hover:opacity-90"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    RUN SIMULATION
                  </>
                )}
              </Button>
              
              {hasRun && (
                <Button onClick={resetSimulation} variant="outline">
                  Reset
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-primary" />
              <span>Prediction Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!hasRun ? (
              <div className="text-center py-12 text-muted-foreground">
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center mx-auto">
                    <Play className="w-8 h-8 opacity-50" />
                  </div>
                  <div>
                    <p className="font-medium mb-1">Ready to Simulate</p>
                    <p className="text-sm">Adjust the parameters and click "RUN SIMULATION" to see the prediction</p>
                  </div>
                </div>
              </div>
            ) : isLoading ? (
              <div className="py-12">
                <LoadingSpinner text="Running prediction model..." />
              </div>
            ) : result ? (
              <div className="space-y-6">
                {/* Prediction Results Header */}
                <div className="text-center space-y-3">
                  <h3 className="text-lg font-semibold">Prediction Results</h3>
                  
                  <div className="grid grid-cols-1 gap-4">
                    <div className="p-4 bg-muted/30 rounded-lg">
                      <h4 className="text-sm font-medium text-muted-foreground mb-2">Final Risk Assessment</h4>
                      <RiskBadge phase={result.final_phase} size="lg" showIcon className="text-lg px-6 py-3" />
                    </div>
                  </div>
                  
                  {/* Model vs Final Comparison */}
                  {result.model_phase !== result.final_phase && (
                    <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                        <h4 className="text-xs font-medium text-muted-foreground mb-2">ML Model</h4>
                        <RiskBadge phase={result.model_phase} />
                    </div>
                    <div>
                        <h4 className="text-xs font-medium text-muted-foreground mb-2">After Safety Rules</h4>
                        <RiskBadge phase={result.final_phase} showIcon />
                    </div>
                    </div>
                  )}
                  
                  {result.rule_override && (
                    <div className="bg-orange/10 border border-orange/30 rounded-lg p-3">
                      <p className="text-sm text-orange font-medium flex items-center">
                        <AlertTriangle className="w-4 h-4 mr-2" />
                        Safety rules overrode ML prediction
                      </p>
                    </div>
                  )}
                </div>

                {/* ML Confidence */}
                {result.ml_probability !== null && (
                  <div>
                    <h4 className="font-semibold mb-3 flex items-center">
                      <Info className="w-4 h-4 mr-2 text-primary" />
                      ML Model Confidence
                    </h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Dropout Probability</span>
                        <span className="font-medium">{(result.ml_probability * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={result.ml_probability * 100} className="h-3" />
                      <p className="text-xs text-muted-foreground">
                        {result.ml_probability < 0.3 ? "Low confidence - rule-based assessment preferred" :
                         result.ml_probability < 0.7 ? "Moderate confidence" :
                         "High confidence prediction"}
                      </p>
                    </div>
                  </div>
                )}

                {/* Risk Factors */}
                {result.override_reason && (
                  <div>
                    <h4 className="font-semibold mb-3 flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-2 text-warning" />
                      Risk Factors
                    </h4>
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="text-sm">{result.override_reason}</p>
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                <div className="bg-primary/5 p-4 rounded-lg border border-primary/20">
                  <h4 className="font-semibold mb-3 text-primary flex items-center">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Recommendations
                  </h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    {result.final_phase === "Red" && (
                      <>
                        <li>• Immediate academic counseling required</li>
                        <li>• Schedule meeting with parents/guardians</li>
                        <li>• Consider academic probation</li>
                        <li>• Implement intensive support program</li>
                      </>
                    )}
                    {result.final_phase === "Orange" && (
                      <>
                        <li>• Enhanced monitoring and support</li>
                        <li>• Regular check-ins with counselor</li>
                        <li>• Additional academic resources</li>
                        <li>• Peer tutoring program enrollment</li>
                      </>
                    )}
                    {result.final_phase === "Yellow" && (
                      <>
                        <li>• Monitor progress closely</li>
                        <li>• Provide additional support if needed</li>
                        <li>• Schedule follow-up in 2 weeks</li>
                      </>
                    )}
                    {result.final_phase === "Green" && (
                      <>
                        <li>• Student is performing well</li>
                        <li>• Continue regular monitoring</li>
                        <li>• Encourage continued good performance</li>
                      </>
                    )}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 mx-auto text-destructive mb-4" />
                <p className="text-destructive font-medium">An error occurred during simulation</p>
                <p className="text-sm text-muted-foreground mt-1">Please try again or check your connection</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      </main>
    </div>
  );
};

export default Simulation;