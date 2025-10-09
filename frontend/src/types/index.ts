export interface Student {
  // Core identification
  enrollment_no: string;
  student_id?: string;
  name?: string; // Real student name from original data
  
  // Personal information
  gender: string;
  age?: number; // Current age
  age_at_enrollment?: number;
  hometown?: string;
  category?: string; // SC, ST, OBC, General, EWS
  
  // Academic information
  attendance: number;
  cgpa: number;
  sgpa?: number; // Current semester GPA
  sgpa1?: number; // Semester 1 GPA
  sgpa2?: number; // Semester 2 GPA
  sgpa3?: number; // Semester 3 GPA
  sgpa4?: number; // Semester 4 GPA
  sgpa5?: number; // Semester 5 GPA
  sgpa6?: number; // Semester 6 GPA
  sgpa7?: number; // Semester 7 GPA
  backlogs: number;
  marks_10th: number;
  marks_12th: number;
  department?: string;
  section?: string;
  course?: string; // Full course name (e.g., "B.B.A.", "B.Tech")
  year_level?: number; // 1, 2, 3, or 4
  year_enrollment?: number; // Year when enrolled (e.g., 2023)
  year_completion?: number; // Expected completion year
  specialization?: string;
  
  // Family and financial information
  father_occupation?: string;
  mother_occupation?: string;
  family_income?: number; // Annual family income
  fees_status?: string; // "Paid", "Partial", "Pending"
  fees_flag: number; // 0 = paid, 1 = unpaid
  suspension?: string; // "Yes", "No"
  suspension_flag: number; // 0 = no suspension, 1 = suspended
  
  // ML Predictions
  final_phase: "Green" | "Yellow" | "Orange" | "Red";
  model_phase?: "Green" | "Yellow" | "Orange" | "Red";
  predicted_phase?: "Green" | "Yellow" | "Orange" | "Red";
  override_reason: string;
  ml_probability: number | null;
  rule_override?: boolean;
  risk_label?: string;
  
  // Computed/alias fields for display
  phase?: "Green" | "Yellow" | "Orange" | "Red"; // Alias for final_phase
  risk_reason?: string; // Alias for override_reason
  prediction?: "Green" | "Yellow" | "Orange" | "Red"; // Another alias
  
  // Debug info (only in development)
  __debug?: {
    raw_backend_data?: any;
    fees_flag_original?: any;
    suspension_flag_original?: any;
  };
}

export interface SimulationData {
  enrollment_no?: string;
  attendance: number;
  cgpa: number;
  backlogs: number;
  marks_10th?: number;
  marks_12th?: number;
  fees_flag: number; // 0 = paid, 1 = unpaid
  suspension_flag: number; // 0 = no suspension, 1 = suspended
  gender?: string;
  email?: string; // Optional email to receive PDF report
}

export interface SimulationResult {
  enrollment_no?: string;
  model_phase: "Green" | "Yellow" | "Orange" | "Red";
  final_phase: "Green" | "Yellow" | "Orange" | "Red";
  override_reason: string;
  ml_probability: number | null;
  rule_override: boolean;
  notification_message?: string; // Notification message for Orange/Red risk
  report_id?: string; // Simulation ID for generated reports
  report_generated?: boolean; // Whether PDF report was generated
  email_sent?: boolean; // Whether report was sent via email
  // Legacy compatibility
  phase?: "Green" | "Yellow" | "Orange" | "Red"; // Alias for final_phase
  risk_reason?: string; // Alias for override_reason
}

export interface AuthContextType {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  user: { username: string } | null;
}

export interface DashboardStats {
  total_students: number;
  green_count: number;
  yellow_count: number;
  orange_count: number;
  red_count: number;
  monitor_count: number; // Yellow only (to be monitored)
  at_risk_count: number; // Orange only (actively at risk)
}

export interface ApiResponse<T> {
  data: T;
  status: string;
  message?: string;
}