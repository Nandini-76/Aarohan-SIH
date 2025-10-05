import axios from 'axios';
import { Student, SimulationData, SimulationResult } from '../types';

// Get API base URL from environment variables with fallback logic
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV ? 'http://127.0.0.1:8000' : 'https://arohann.onrender.com');

console.log('API Base URL:', API_BASE_URL); // Debug log

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false, // Set to false for CORS simplicity in development
  timeout: 60000, // 60 second timeout for ML predictions and Firebase operations
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('Making API request to:', config.baseURL + config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API response received:', response.status);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    if (error.code === 'ERR_NETWORK') {
      console.error('Network error - check if backend is running on:', API_BASE_URL);
    }
    throw error;
  }
);

export const studentApi = {
  // Get all students
  getAllStudents: async (): Promise<Student[]> => {
    const response = await api.get('/students');
    const students = response.data.students || [];
    
    // Transform backend data to frontend format with consistent field mapping
    return students.map((student: any) => ({
      // Core identification
      enrollment_no: student.enrollment_no,
      student_id: student.student_id || student.enrollment_no,
      name: student.name || generateStudentName(student.enrollment_no),
      department: student.department,
      
      // Academic data
      attendance: student.attendance,
      cgpa: student.cgpa,
      backlogs: student.backlogs,
      marks_10th: student.marks_10th,
      marks_12th: student.marks_12th,
      
      // Flags (ensure proper numeric format)
      fees_flag: Number(student.fees_flag), // 0 = paid, 1 = unpaid
      suspension_flag: Number(student.suspension_flag), // 0 = no suspension, 1 = suspended
      
      // Demographics
      gender: student.gender,
      age_at_enrollment: student.age_at_enrollment,
      category: student.category,
      
      // Prediction results
      final_phase: student.final_phase || student.prediction,
      phase: student.final_phase || student.prediction, // Alias for compatibility
      model_phase: student.model_phase,
      override_reason: student.override_reason,
      risk_reason: student.override_reason, // Alias for compatibility
      risk_label: student.risk_label,
      ml_probability: student.ml_probability,
      rule_override: student.rule_override,
      
      // Debug info
      __debug: process.env.NODE_ENV === 'development' ? {
        raw_backend_data: student,
        fees_flag_original: student.fees_flag,
        suspension_flag_original: student.suspension_flag
      } : undefined
    }));
  },

  // Get single student by enrollment number
  getStudent: async (enrollmentNo: string): Promise<Student> => {
    const response = await api.get(`/students/${enrollmentNo}`);
    const student = response.data;
    
    // Transform backend data to frontend format with consistent field mapping
    return {
      // Core identification
      enrollment_no: student.enrollment_no,
      student_id: student.student_id || student.enrollment_no,
      name: student.name || generateStudentName(student.enrollment_no),
      department: student.department,
      
      // Academic data
      attendance: student.attendance,
      cgpa: student.cgpa,
      backlogs: student.backlogs,
      marks_10th: student.marks_10th,
      marks_12th: student.marks_12th,
      
      // Flags (ensure proper numeric format)
      fees_flag: Number(student.fees_flag), // 0 = paid, 1 = unpaid
      suspension_flag: Number(student.suspension_flag), // 0 = no suspension, 1 = suspended
      
      // Demographics
      gender: student.gender,
      age_at_enrollment: student.age_at_enrollment,
      category: student.category,
      
      // Prediction results
      final_phase: student.final_phase || student.prediction,
      phase: student.final_phase || student.prediction, // Alias for compatibility
      model_phase: student.model_phase,
      override_reason: student.override_reason,
      risk_reason: student.override_reason, // Alias for compatibility
      risk_label: student.risk_label,
      ml_probability: student.ml_probability,
      rule_override: student.rule_override,
      
      // Debug info
      __debug: process.env.NODE_ENV === 'development' ? {
        raw_backend_data: student,
        fees_flag_original: student.fees_flag,
        suspension_flag_original: student.suspension_flag
      } : undefined
    };
  },

  // Simulate student risk prediction
  simulate: async (data: SimulationData): Promise<SimulationResult> => {
    const response = await api.post('/simulate', data);
    const result = response.data;
    
    // Transform response to include legacy fields
    return {
      ...result,
      phase: result.final_phase, // Alias for compatibility
      risk_reason: result.override_reason, // Alias for compatibility
    };
  },

  // Get prediction for student data
  predict: async (studentData: any): Promise<any> => {
    const response = await api.post('/predict', studentData);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/');
    return response.data;
  },
};

// Helper function to generate display names from enrollment numbers
function generateStudentName(enrollmentNo: string): string {
  // Extract number from enrollment (e.g., "2023ENG001" -> "001")
  const match = enrollmentNo.match(/(\d+)$/);
  const num = match ? parseInt(match[1]) : 1;
  
  // Generate realistic names based on enrollment number
  const firstNames = [
    'Aarav', 'Ananya', 'Arjun', 'Diya', 'Ishaan', 'Kavya', 'Kiran', 'Meera',
    'Nikhil', 'Priya', 'Rahul', 'Riya', 'Rohan', 'Sakshi', 'Siddharth', 'Sneha',
    'Varun', 'Vani', 'Yash', 'Zara', 'Aditya', 'Aditi', 'Akash', 'Bhavya',
    'Charan', 'Deepika', 'Eshaan', 'Fathima', 'Gaurav', 'Harini'
  ];
  
  const lastNames = [
    'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Reddy', 'Patel', 'Shah',
    'Jain', 'Agarwal', 'Mehta', 'Chopra', 'Malhotra', 'Khanna', 'Rao',
    'Iyer', 'Nair', 'Pillai', 'Menon', 'Krishnan', 'Sundaram', 'Raman',
    'Prasad', 'Srinivas', 'Venkat', 'Mohan', 'Suresh', 'Ramesh', 'Dinesh', 'Ganesh'
  ];
  
  const firstName = firstNames[(num - 1) % firstNames.length];
  const lastName = lastNames[Math.floor((num - 1) / firstNames.length) % lastNames.length];
  
  return `${firstName} ${lastName}`;
}

export default api;