export interface Student {
  enrollment_no: string;
  attendance: number;
  cgpa: number;
  backlogs: number;
  marks_10th: number;
  marks_12th: number;
  fees_flag: number; // 0 = paid, 1 = unpaid
  suspension_flag: number; // 0 = no suspension, 1 = suspended
  gender: string;
  age_at_enrollment?: number;
  category?: string;
  department?: string;
  final_phase: "Green" | "Yellow" | "Orange" | "Red";
  override_reason: string;
  ml_probability: number | null;
  // Computed fields for display
  name?: string; // We'll generate this from enrollment_no
  phase?: "Green" | "Yellow" | "Orange" | "Red"; // Alias for final_phase
  risk_reason?: string; // Alias for override_reason
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
}

export interface SimulationResult {
  enrollment_no?: string;
  model_phase: "Green" | "Yellow" | "Orange" | "Red";
  final_phase: "Green" | "Yellow" | "Orange" | "Red";
  override_reason: string;
  ml_probability: number | null;
  rule_override: boolean;
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