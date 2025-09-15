import axios from 'axios';
import { Student, SimulationData, SimulationResult } from '../types';

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export const studentApi = {
  // Get all students
  getAllStudents: async (): Promise<Student[]> => {
    const response = await api.get('/students');
    const students = response.data.students || [];
    
    // Transform backend data to frontend format
    return students.map((student: any) => ({
      ...student,
      name: generateStudentName(student.enrollment_no), // Generate display name
      phase: student.final_phase, // Alias for compatibility
      risk_reason: student.override_reason, // Alias for compatibility
      fees_flag: student.fees_flag, // Keep as number for backend compatibility
      suspension_flag: student.suspension_flag, // Keep as number for backend compatibility
    }));
  },

  // Get single student by enrollment number
  getStudent: async (enrollmentNo: string): Promise<Student> => {
    const response = await api.get(`/students/${enrollmentNo}`);
    const student = response.data;
    
    // Transform backend data to frontend format
    return {
      ...student,
      name: generateStudentName(student.enrollment_no),
      phase: student.final_phase,
      risk_reason: student.override_reason,
      fees_flag: student.fees_flag,
      suspension_flag: student.suspension_flag,
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