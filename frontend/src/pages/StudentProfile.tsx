import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { 
  ArrowLeft, User, GraduationCap, CreditCard, Users, Phone, 
  TrendingUp, AlertCircle, CheckCircle, Calendar, MapPin 
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Separator } from '../components/ui/separator';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { studentApi } from '../services/api';
import { Student } from '../types';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';
import SiteHeader from '../components/SiteHeader';

const StudentProfile: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  const { enrollmentNo } = useParams<{ enrollmentNo: string }>();
  const [student, setStudent] = useState<Student | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (enrollmentNo) {
      fetchStudent(enrollmentNo);
    }
  }, [enrollmentNo]);

  const fetchStudent = async (id: string) => {
    try {
      setIsLoading(true);
      const data = await studentApi.getStudent(id);
      setStudent(data);
    } catch (error) {
      console.error('Failed to fetch student:', error);
      toast({
        title: "Error", 
        description: "Failed to fetch student data. Please check if the backend server is running.",
        variant: "destructive",
      });
      setStudent(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskLevel = (phase: string) => {
    switch (phase) {
      case "Green": return { level: "Low Risk", color: "text-success", bgColor: "bg-success/10" };
      case "Yellow": return { level: "Medium Risk", color: "text-warning", bgColor: "bg-warning/10" };
      case "Orange": return { level: "High Risk", color: "text-orange", bgColor: "bg-orange/10" };
      case "Red": return { level: "Critical Risk", color: "text-destructive", bgColor: "bg-destructive/10" };
      default: return { level: "Unknown", color: "text-muted-foreground", bgColor: "bg-muted/10" };
    }
  };

  const getAttendanceStatus = (attendance: number) => {
    if (attendance >= 85) return { status: "Excellent", color: "text-success" };
    if (attendance >= 75) return { status: "Good", color: "text-success" };
    if (attendance >= 65) return { status: "Average", color: "text-warning" };
    return { status: "Poor", color: "text-destructive" };
  };

  const getCGPAStatus = (cgpa: number) => {
    if (cgpa >= 8.5) return { status: "Outstanding", color: "text-success" };
    if (cgpa >= 7.5) return { status: "Very Good", color: "text-success" };
    if (cgpa >= 6.5) return { status: "Good", color: "text-warning" };
    if (cgpa >= 5.5) return { status: "Average", color: "text-warning" };
    return { status: "Below Average", color: "text-destructive" };
  };
  if (isLoading) {
    const bgStyle: React.CSSProperties = {
      background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                   radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                   linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
    };
    return (
      <div className="min-h-screen text-white" style={bgStyle}>
        <SiteHeader />
        <main className="container mx-auto px-4 md:px-8 py-8 md:py-12">
          <div className="flex items-center justify-center h-96">
            <LoadingSpinner size="lg" text="Loading student profile..." />
          </div>
        </main>
      </div>
    );
  }

  if (!student) {
    const bgStyle: React.CSSProperties = {
      background: `radial-gradient(1200px 800px at -10% -10%, #8dd5ff55 0%, transparent 60%),
                   radial-gradient(1200px 800px at 110% 20%, #a78bfa40 0%, transparent 55%),
                   linear-gradient(135deg, #94c5ff 0%, #2b6cb0 40%, #0d3b66 100%)`,
    };
    return (
      <div className="min-h-screen text-white" style={bgStyle}>
        <SiteHeader />
        <main className="container mx-auto px-4 md:px-8 py-8 md:py-12 space-y-6">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className="p-2"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-3xl font-bold">Student Not Found</h1>
          </div>
          
          <Card className="bg-white text-foreground">
            <CardContent className="text-center py-12">
              <Users className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
              <h2 className="text-xl font-semibold text-muted-foreground mb-2">Student not found</h2>
              <p className="text-muted-foreground mb-6">
                The student with enrollment number "{enrollmentNo}" could not be found.
              </p>
              <Button onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const riskInfo = getRiskLevel(student.phase || "Green");
  const attendanceInfo = getAttendanceStatus(student.attendance);
  const cgpaInfo = getCGPAStatus(student.cgpa);
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
            <h1 className="text-3xl font-bold">{student.name || "Student Profile"}</h1>
            <p className="text-muted-foreground">
              {student.enrollment_no} • {student.department || "Unknown Department"}
            </p>
          </div>
        </div>
        <div className="text-right">
          <RiskBadge phase={student.phase || "Green"} size="lg" showIcon />
          <p className="text-sm text-muted-foreground mt-1">{riskInfo.level}</p>
        </div>
      </div>

      {/* Risk Assessment Alert */}
      {student.risk_reason && student.phase !== "Green" && (
        <Card className={cn("border-2", 
          student.phase === "Red" ? "border-destructive bg-destructive/5" :
          student.phase === "Orange" ? "border-orange bg-orange/5" :
          "border-warning bg-warning/5"
        )}>
          <CardContent className="p-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className={cn("w-5 h-5 mt-0.5", 
                student.phase === "Red" ? "text-destructive" :
                student.phase === "Orange" ? "text-orange" :
                "text-warning"
              )} />
              <div>
                <p className="font-semibold mb-1">Risk Factors Identified</p>
                <p className="text-sm text-muted-foreground">{student.risk_reason}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Academic Information */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <GraduationCap className="h-5 w-5 text-primary" />
              <span>Academic Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Academic Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-muted-foreground">Attendance</label>
                  <span className={cn("text-sm font-medium", attendanceInfo.color)}>
                    {attendanceInfo.status}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">{student.attendance}%</span>
                    <span className="text-sm text-muted-foreground">Target: 75%</span>
                  </div>
                  <Progress value={student.attendance} className="h-2" />
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-muted-foreground">CGPA</label>
                  <span className={cn("text-sm font-medium", cgpaInfo.color)}>
                    {cgpaInfo.status}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">{student.cgpa}</span>
                    <span className="text-sm text-muted-foreground">Max: 10.0</span>
                  </div>
                  <Progress value={(student.cgpa / 10) * 100} className="h-2" />
                </div>
              </div>
            </div>
            
            <Separator />
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Active Backlogs</label>
                <p className={cn("text-xl font-semibold", 
                  student.backlogs > 3 ? "text-destructive" : 
                  student.backlogs > 0 ? "text-warning" : "text-success"
                )}>
                  {student.backlogs}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">10th Grade</label>
                <p className="text-xl font-semibold">{student.marks_10th}%</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">12th Grade</label>
                <p className="text-xl font-semibold">{student.marks_12th}%</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Year</label>
                <p className="text-xl font-semibold">{student.enrollment_no?.slice(0, 4) || "N/A"}</p>
              </div>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {student.suspension_flag > 0 && (
                <Badge variant="destructive">Academic Suspension</Badge>
              )}
              {student.fees_flag === 0 && (
                <Badge variant="secondary" className="bg-success/10 text-success">Fees Paid</Badge>
              )}
              {student.fees_flag > 0 && (
                <Badge variant="destructive">Outstanding Fees</Badge>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Risk Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-primary" />
              <span>Risk Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className={cn("p-4 rounded-lg border-2", riskInfo.bgColor, 
              student.phase === "Red" ? "border-destructive" :
              student.phase === "Orange" ? "border-orange" :
              student.phase === "Yellow" ? "border-warning" :
              "border-success"
            )}>
              <div className="text-center space-y-2">
                <RiskBadge phase={student.phase || "Green"} size="lg" showIcon />
                <p className={cn("font-semibold", riskInfo.color)}>{riskInfo.level}</p>
              </div>
            </div>
            
            {student.risk_reason && (
              <div>
                <h4 className="font-semibold mb-2 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2 text-warning" />
                  Risk Factors
                </h4>
                <div className="bg-muted p-3 rounded-lg">
                  <p className="text-sm">{student.risk_reason}</p>
                </div>
              </div>
            )}
            
            {student.ml_probability !== null && (
              <div>
                <h4 className="font-semibold mb-2">ML Confidence Score</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Dropout Probability</span>
                    <span className="font-medium">{(student.ml_probability * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={student.ml_probability * 100} className="h-2" />
                </div>
              </div>
            )}
            
            <Button 
              onClick={() => navigate('/simulation', { state: { student } })}
              className="w-full bg-gradient-secondary hover:opacity-90"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Run Risk Simulation
            </Button>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5 text-primary" />
              <span>Personal Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Gender</label>
                <p className="text-lg font-medium">{student.gender}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Age at Enrollment</label>
                <p className="text-lg font-medium">{student.age_at_enrollment || "N/A"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Category</label>
                <Badge variant="outline">{student.category || "General"}</Badge>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Department</label>
                <Badge variant="secondary">{student.department || "N/A"}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Financial Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CreditCard className="h-5 w-5 text-primary" />
              <span>Financial Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Fee Status</label>
                <div className="flex items-center space-x-2 mt-1">
                  {student.fees_flag > 0 ? (
                    <>
                      <div className="w-2 h-2 rounded-full bg-destructive"></div>
                      <span className="text-destructive font-medium">Outstanding</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4 text-success" />
                      <span className="text-success font-medium">Paid</span>
                    </>
                  )}
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground">Previous Academic Records</label>
                <div className="grid grid-cols-2 gap-2 mt-1">
                  <div className="text-center p-2 bg-muted/50 rounded">
                    <p className="text-xs text-muted-foreground">10th Grade</p>
                    <p className="font-semibold">{student.marks_10th}%</p>
                  </div>
                  <div className="text-center p-2 bg-muted/50 rounded">
                    <p className="text-xs text-muted-foreground">12th Grade</p>
                    <p className="font-semibold">{student.marks_12th}%</p>
                  </div>
                </div>
              </div>
            </div>
            
            {student.fees_flag > 0 && (
              <div className="p-3 bg-destructive/10 rounded-lg border border-destructive/20">
                <p className="text-sm text-destructive font-medium">
                  ⚠️ Outstanding fee payment may affect academic progression
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      {student.phase !== "Green" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-primary" />
              <span>Recommended Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-3 text-sm">
              {student.phase === "Red" && (
                <>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-destructive mt-2"></div>
                    <span>Immediate academic counseling required</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-destructive mt-2"></div>
                    <span>Schedule meeting with parents/guardians</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-destructive mt-2"></div>
                    <span>Consider academic probation or intervention</span>
                  </li>
                </>
              )}
              {student.phase === "Orange" && (
                <>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-orange mt-2"></div>
                    <span>Enhanced monitoring and support</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-orange mt-2"></div>
                    <span>Regular check-ins with academic counselor</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-orange mt-2"></div>
                    <span>Provide additional academic resources</span>
                  </li>
                </>
              )}
              {student.phase === "Yellow" && (
                <>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-warning mt-2"></div>
                    <span>Monitor progress closely</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-warning mt-2"></div>
                    <span>Provide additional support if needed</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full bg-warning mt-2"></div>
                    <span>Schedule follow-up in 2 weeks</span>
                  </li>
                </>
              )}
            </ul>
          </CardContent>
        </Card>
      )}
      </main>
    </div>
  );
};

export default StudentProfile;