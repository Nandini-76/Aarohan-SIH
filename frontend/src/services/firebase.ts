/**
 * Firebase Realtime Database Configuration
 * Enables the frontend to display latest prediction data even when backend is sleeping
 * 
 * This service connects to Firebase Realtime Database to listen for updates
 * from the backend. When the backend (on Render free tier) goes to sleep,
 * judges and viewers can still see the last stored predictions.
 */

import { initializeApp, FirebaseApp } from "firebase/app";
import { getDatabase, ref, onValue, off, Database, DatabaseReference } from "firebase/database";

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

let app: FirebaseApp | null = null;
let database: Database | null = null;

/**
 * Initialize Firebase app and database
 * Call this once at app startup
 */
export const initFirebase = (): boolean => {
  try {
    // Check if environment variables are configured
    if (!firebaseConfig.apiKey || !firebaseConfig.databaseURL) {
      console.warn("Firebase environment variables not configured");
      return false;
    }

    // Initialize Firebase app
    app = initializeApp(firebaseConfig);
    database = getDatabase(app);
    
    console.log("Firebase initialized successfully");
    return true;
  } catch (error) {
    console.error("Failed to initialize Firebase:", error);
    return false;
  }
};

/**
 * Listen to latest data from Firebase Realtime Database
 * This data is updated by the backend whenever a simulation runs
 * 
 * @param callback Function to call when data changes
 * @returns Unsubscribe function to stop listening
 */
export const listenToLatestData = (callback: (data: any) => void): (() => void) => {
  if (!database) {
    console.warn("Firebase not initialized. Call initFirebase() first.");
    return () => {}; // Return no-op unsubscribe
  }

  const dataRef: DatabaseReference = ref(database, "latestData");
  
  // Set up real-time listener
  onValue(dataRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  }, (error) => {
    console.error("Firebase listener error:", error);
    callback(null); // Pass null on error
  });

  // Return unsubscribe function
  return () => {
    off(dataRef);
  };
};

/**
 * Listen to student-specific prediction data
 * 
 * @param studentId Student enrollment number or ID
 * @param callback Function to call when data changes
 * @returns Unsubscribe function
 */
export const listenToStudentData = (studentId: string, callback: (data: any) => void): (() => void) => {
  if (!database) {
    console.warn("Firebase not initialized. Call initFirebase() first.");
    return () => {};
  }

  const studentRef: DatabaseReference = ref(database, `students/${studentId}`);
  
  onValue(studentRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  }, (error) => {
    console.error("Firebase student listener error:", error);
    callback(null);
  });

  return () => {
    off(studentRef);
  };
};

/**
 * Listen to batch predictions data
 * 
 * @param callback Function to call when batch data changes
 * @returns Unsubscribe function
 */
export const listenToBatchPredictions = (callback: (data: any) => void): (() => void) => {
  if (!database) {
    console.warn("Firebase not initialized. Call initFirebase() first.");
    return () => {};
  }

  const batchRef: DatabaseReference = ref(database, "batchPredictions");
  
  onValue(batchRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  }, (error) => {
    console.error("Firebase batch listener error:", error);
    callback(null);
  });

  return () => {
    off(batchRef);
  };
};

/**
 * Listen to any custom path in Firebase
 * 
 * @param path Firebase path (e.g., "analytics/summary")
 * @param callback Function to call when data changes
 * @returns Unsubscribe function
 */
export const listenToPath = (path: string, callback: (data: any) => void): (() => void) => {
  if (!database) {
    console.warn("Firebase not initialized. Call initFirebase() first.");
    return () => {};
  }

  const customRef: DatabaseReference = ref(database, path);
  
  onValue(customRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  }, (error) => {
    console.error(`Firebase listener error for path ${path}:`, error);
    callback(null);
  });

  return () => {
    off(customRef);
  };
};

/**
 * Fetch all students data from Firebase (one-time read)
 * This is used as a fallback when the backend is unavailable
 * 
 * @returns Promise with students array
 */
export const getAllStudentsFromFirebase = async (): Promise<any[]> => {
  if (!database) {
    console.warn("Firebase not initialized. Call initFirebase() first.");
    throw new Error("Firebase not initialized");
  }

  return new Promise((resolve, reject) => {
    const studentsRef: DatabaseReference = ref(database, "students");
    
    // Get data once (not a listener)
    onValue(studentsRef, (snapshot) => {
      const data = snapshot.val();
      
      if (data) {
        // Convert Firebase object to array
        const studentsArray = Object.values(data);
        console.log(`Fetched ${studentsArray.length} students from Firebase`);
        resolve(studentsArray);
      } else {
        console.warn("No students data found in Firebase");
        resolve([]);
      }
      
      // Unsubscribe immediately after first read
      off(studentsRef);
    }, (error) => {
      console.error("Firebase fetch error:", error);
      reject(error);
    });
  });
};

/**
 * Fetch a single student from Firebase (one-time read)
 * 
 * @param enrollmentNo Student enrollment number
 * @returns Promise with student data
 */
export const getStudentFromFirebase = async (enrollmentNo: string): Promise<any> => {
  if (!database) {
    console.warn("Firebase not initialized. Call initFirebase() first.");
    throw new Error("Firebase not initialized");
  }

  return new Promise((resolve, reject) => {
    const studentRef: DatabaseReference = ref(database, `students/${enrollmentNo}`);
    
    onValue(studentRef, (snapshot) => {
      const data = snapshot.val();
      
      if (data) {
        console.log(`Fetched student ${enrollmentNo} from Firebase`);
        resolve(data);
      } else {
        reject(new Error(`Student ${enrollmentNo} not found in Firebase`));
      }
      
      // Unsubscribe immediately
      off(studentRef);
    }, (error) => {
      console.error("Firebase fetch error:", error);
      reject(error);
    });
  });
};

/**
 * Check if Firebase is initialized and configured
 */
export const isFirebaseConfigured = (): boolean => {
  return app !== null && database !== null;
};

/**
 * Get Firebase configuration status for debugging
 */
export const getFirebaseStatus = () => {
  return {
    initialized: app !== null,
    databaseConnected: database !== null,
    hasApiKey: !!firebaseConfig.apiKey,
    hasDatabaseUrl: !!firebaseConfig.databaseURL,
    projectId: firebaseConfig.projectId || "not_configured"
  };
};

// Auto-initialize Firebase on module load
try {
  initFirebase();
} catch (error) {
  console.error("Auto-initialization of Firebase failed:", error);
}
