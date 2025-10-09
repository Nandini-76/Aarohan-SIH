import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, RefreshCw, Sliders, AlertTriangle, Info, CheckCircle, Mail } from 'lucide-react';
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
import { Skeleton } from '../components/ui/skeleton';
import { studentApi } from '../services/api';
import { SimulationData, SimulationResult, Student } from '../types';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';
import SiteHeader from '../components/SiteHeader';

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
      
      // Debug logging to see what we're receiving
      console.log('🔍 Simulation result received:', result);
      console.log('🔍 Notification message:', result.notification_message);
      console.log('🔍 Final phase:', result.final_phase);
      
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
        email: '',
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
        email: '',
      });
    }
    setResult(null);
    setHasRun(false);
    setRealTimeMode(false);
  };

  const bgStyle: React.CSSProperties = {
    background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                 radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                 linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
  };

  return (
    <div className="min-h-screen text-white" style={bgStyle}>
      <SiteHeader />
      <main className="container mx-auto px-4 md:px-8 py-4 md:py-6 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="p-1.5"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center space-x-2">
              <Sliders className="h-6 w-6 text-primary" />
              <span>AAROHAN Risk Simulation</span>
            </h1>
            <p className="text-sm text-white/90">
              AI-powered dropout risk prediction and analysis
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Label htmlFor="realtime" className="text-xs">Real-time</Label>
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
          <CardContent className="p-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
                <Info className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">Simulating for: {studentFromProfile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {studentFromProfile.enrollment_no} • {studentFromProfile.department}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Input Parameters */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-base">
              <Sliders className="h-4 w-4 text-primary" />
              <span>Simulation Parameters</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Enrollment Number (if not from profile) */}
            {!studentFromProfile && (
              <div className="space-y-1">
                <Label htmlFor="enrollment" className="text-xs">Enrollment Number (Optional)</Label>
                <Input
                  id="enrollment"
                  type="text"
                  placeholder="e.g., 2023ENG001"
                  value={formData.enrollment_no || ''}
                  onChange={(e) => handleInputChange('enrollment_no', e.target.value)}
                  className="h-8 text-sm"
                />
              </div>
            )}

            {/* Compact Grid for Main Metrics */}
            <div className="grid grid-cols-2 gap-3">
              {/* Attendance */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label htmlFor="attendance" className="text-xs">Attendance</Label>
                  <span className="text-xs font-medium">{formData.attendance}%</span>
                </div>
                <Slider
                  value={[formData.attendance]}
                  onValueChange={(value) => handleInputChange('attendance', value[0])}
                  max={100}
                  min={0}
                  step={1}
                  className="w-full"
                />
                {formData.attendance < 70 && (
                  <p className="text-[10px] text-destructive">Below 70%</p>
                )}
              </div>

              {/* CGPA */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label htmlFor="cgpa" className="text-xs">CGPA</Label>
                  <span className="text-xs font-medium">{formData.cgpa.toFixed(1)}</span>
                </div>
                <Slider
                  value={[formData.cgpa]}
                  onValueChange={(value) => handleInputChange('cgpa', value[0])}
                  max={10}
                  min={0}
                  step={0.1}
                  className="w-full"
                />
                {formData.cgpa < 5 && (
                  <p className="text-[10px] text-destructive">Below Average</p>
                )}
              </div>

              {/* Backlogs */}
              <div className="space-y-1">
                <Label htmlFor="backlogs" className="text-xs">Backlogs</Label>
                <Input
                  id="backlogs"
                  type="number"
                  min="0"
                  max="15"
                  value={formData.backlogs}
                  onChange={(e) => handleInputChange('backlogs', Number(e.target.value))}
                  className="h-8 text-sm"
                />
                {formData.backlogs > 3 && (
                  <p className="text-[10px] text-destructive">⚠️ High</p>
                )}
              </div>

              {/* Gender */}
              <div className="space-y-1">
                <Label htmlFor="gender" className="text-xs">Gender</Label>
                <Select
                  value={formData.gender}
                  onValueChange={(value) => handleInputChange('gender', value)}
                >
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue placeholder="Select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">Male</SelectItem>
                    <SelectItem value="F">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* 10th Marks */}
              <div className="space-y-1">
                <Label htmlFor="marks-10th" className="text-xs">10th Marks (%)</Label>
                <Input
                  id="marks-10th"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.marks_10th}
                  onChange={(e) => handleInputChange('marks_10th', Number(e.target.value))}
                  className="h-8 text-sm"
                />
              </div>

              {/* 12th Marks */}
              <div className="space-y-1">
                <Label htmlFor="marks-12th" className="text-xs">12th Marks (%)</Label>
                <Input
                  id="marks-12th"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.marks_12th}
                  onChange={(e) => handleInputChange('marks_12th', Number(e.target.value))}
                  className="h-8 text-sm"
                />
              </div>
            </div>

            <Separator className="my-2" />

            {/* Flags - More Compact */}
            <div className="space-y-2">
              <h3 className="font-semibold text-xs text-muted-foreground uppercase tracking-wide">
                Risk Factors
              </h3>
              
              <div className="flex items-center justify-between py-1">
                <Label htmlFor="fees-flag" className="text-xs font-medium">Outstanding Fees</Label>
                <Switch
                  id="fees-flag"
                  checked={Boolean(formData.fees_flag)}
                  onCheckedChange={(checked) => handleInputChange('fees_flag', checked ? 1 : 0)}
                />
              </div>

              <div className="flex items-center justify-between py-1">
                <Label htmlFor="suspension-flag" className="text-xs font-medium">Academic Suspension</Label>
                <Switch
                  id="suspension-flag"
                  checked={Boolean(formData.suspension_flag)}
                  onCheckedChange={(checked) => handleInputChange('suspension_flag', checked ? 1 : 0)}
                />
              </div>
            </div>

            <Separator className="my-2" />

            {/* Email Input for Report */}
            <div className="space-y-1">
              <Label htmlFor="email" className="text-xs flex items-center space-x-1">
                <span>Email Address (Optional)</span>
                <span className="text-muted-foreground">- Receive PDF report for Orange/Red risk</span>
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="e.g., student@example.com"
                value={formData.email || ''}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="h-8 text-sm"
              />
              <p className="text-[10px] text-muted-foreground">
                📧 Report will be emailed if provided, or available for download
              </p>
            </div>

            {/* Action Buttons - Sticky at bottom */}
            <div className="flex space-x-2 pt-3 sticky bottom-0 bg-card pb-2">
              <Button
                onClick={() => runSimulation()}
                disabled={isLoading}
                className="flex-1 bg-gradient-primary hover:opacity-90 h-10"
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
                <Button onClick={resetSimulation} variant="outline" className="h-10">
                  Reset
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-base">
              <AlertTriangle className="h-4 w-4 text-primary" />
              <span>Prediction Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!hasRun ? (
              <div className="text-center py-8 text-muted-foreground">
                <div className="space-y-3">
                  <div className="w-12 h-12 bg-muted/50 rounded-full flex items-center justify-center mx-auto">
                    <Play className="w-6 h-6 opacity-50" />
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-1">Ready to Simulate</p>
                    <p className="text-xs">Adjust the parameters and click "RUN SIMULATION"</p>
                  </div>
                </div>
              </div>
            ) : isLoading ? (
              <div className="py-12 space-y-6">
                <div className="text-center space-y-3">
                  <Skeleton variant="text" className="h-6 w-48 mx-auto" />
                  <div className="space-y-4">
                    <div className="p-6 bg-muted/30 rounded-lg space-y-3">
                      <Skeleton variant="text" className="h-4 w-32 mx-auto" />
                      <Skeleton variant="button" className="h-12 w-32 mx-auto" />
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Array.from({ length: 4 }).map((_, index) => (
                    <div key={index} className="p-4 bg-muted/20 rounded-lg space-y-2">
                      <Skeleton variant="text" className="h-4 w-24" />
                      <Skeleton variant="text" className="h-8 w-full" />
                      <Skeleton variant="text" className="h-3 w-3/4" />
                    </div>
                  ))}
                </div>
                
                <div className="text-center">
                  <LoadingSpinner text="Running prediction model..." />
                </div>
              </div>
            ) : result ? (
              <div className="space-y-3">
                {/* Prediction Results Header */}
                <div className="text-center space-y-2">
                  <h3 className="text-base font-semibold">Prediction Results</h3>
                  
                  <div className="grid grid-cols-1 gap-2">
                    <div className="p-3 bg-muted/30 rounded-lg">
                      <h4 className="text-xs font-medium text-muted-foreground mb-1.5">Final Risk Assessment</h4>
                      <RiskBadge phase={result.final_phase} size="lg" showIcon className="text-base px-4 py-2" />
                    </div>
                  </div>
                  
                  {/* Model vs Final Comparison */}
                  {result.model_phase !== result.final_phase && (
                    <div className="grid grid-cols-2 gap-2 mt-2">
                    <div>
                        <h4 className="text-[10px] font-medium text-muted-foreground mb-1">ML Model</h4>
                        <RiskBadge phase={result.model_phase} />
                    </div>
                    <div>
                        <h4 className="text-[10px] font-medium text-muted-foreground mb-1">After Safety Rules</h4>
                        <RiskBadge phase={result.final_phase} showIcon />
                    </div>
                    </div>
                  )}
                  
                  {result.rule_override && (
                    <div className="bg-orange/10 border border-orange/30 rounded-lg p-2">
                      <p className="text-xs text-orange font-medium flex items-center">
                        <AlertTriangle className="w-3 h-3 mr-1.5" />
                        Safety rules overrode ML prediction
                      </p>
                    </div>
                  )}
                </div>

                {/* Risk Factors */}
                {result.override_reason && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2 flex items-center">
                      <AlertTriangle className="w-3 h-3 mr-1.5 text-warning" />
                      Risk Factors
                    </h4>
                    <div className="bg-muted p-2.5 rounded-lg">
                      <p className="text-xs">{result.override_reason}</p>
                    </div>
                  </div>
                )}

                {/* Notification Alert */}
                {result.notification_message && (result.final_phase === "Orange" || result.final_phase === "Red") && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2 flex items-center">
                      <Info className="w-3 h-3 mr-1.5 text-blue-600" />
                      Notification Sent
                    </h4>
                    <div className="bg-blue-50 border border-blue-200 p-2.5 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <div className="flex-shrink-0">
                          <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                        </div>
                        <div className="flex-1">
                          <p className="text-xs text-blue-800 font-medium mb-0.5">
                            Alert Notification Triggered
                          </p>
                          <p className="text-xs text-blue-700">
                            {result.notification_message}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Report Generation Status */}
                {result.report_generated && (result.final_phase === "Orange" || result.final_phase === "Red") && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2 flex items-center">
                      <CheckCircle className="w-3 h-3 mr-1.5 text-green-600" />
                      PDF Report Generated
                    </h4>
                    <div className="bg-green-50 border border-green-200 p-3 rounded-lg space-y-2">
                      <div className="flex items-start space-x-2">
                        <div className="flex-shrink-0">
                          <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                        </div>
                        <div className="flex-1">
                          <p className="text-xs text-green-800 font-medium mb-0.5">
                            Multilingual Report Available
                          </p>
                          <p className="text-xs text-green-700 mb-2">
                            Report generated in English, Hindi, and Rajasthani
                          </p>
                          
                          {result.email_sent && formData.email && (
                            <div className="flex items-center space-x-1 text-xs text-green-700 mb-2">
                              <CheckCircle className="w-3 h-3" />
                              <span>Report sent to {formData.email}</span>
                            </div>
                          )}
                          
                          <div className="flex flex-wrap gap-2 mt-2">
                            <a
                              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/report/${result.report_id}?language=en`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                            >
                              📄 English Report
                            </a>
                            <a
                              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/report/${result.report_id}?language=hi`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                            >
                              📄 हिंदी रिपोर्ट
                            </a>
                            <a
                              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/report/${result.report_id}?language=rj`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                            >
                              📄 राजस्थानी रिपोर्ट
                            </a>
                            <a
                              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/report/${result.report_id}/all`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-3 py-1.5 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 transition-colors"
                            >
                              📦 Download All (ZIP)
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Debug Info - Remove this after testing */}
                {result && (
                  <div className="bg-gray-100 p-1.5 rounded text-[10px]">
                    <strong>Debug:</strong> Phase: {result.final_phase}, 
                    Has notification: {result.notification_message ? 'Yes' : 'No'}, 
                    Message: {result.notification_message || 'None'},
                    Report ID: {result.report_id || 'None'},
                    Report Generated: {result.report_generated ? 'Yes' : 'No'},
                    Email Sent: {result.email_sent ? 'Yes' : 'No'}
                  </div>
                )}

                {/* Recommendations */}
                <div className="bg-primary/5 p-3 rounded-lg border border-primary/20">
                  <h4 className="text-sm font-semibold mb-2 text-primary flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1.5" />
                    Recommendations
                  </h4>
                  <ul className="text-xs space-y-0.5 text-muted-foreground">
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
              <div className="text-center py-8">
                <AlertTriangle className="w-10 h-10 mx-auto text-destructive mb-3" />
                <p className="text-sm text-destructive font-medium">An error occurred during simulation</p>
                <p className="text-xs text-muted-foreground mt-1">Please try again or check your connection</p>
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