/**
 * MongoDB Data API Integration
 * 
 * This service fetches data directly from MongoDB using the Data API.
 * This ensures the frontend can always display data even when the backend is inactive.
 * 
 * Setup:
 * 1. Create a MongoDB Data API in Atlas Console
 * 2. Get your App ID and API Key
 * 3. Add them to .env file
 */

interface MongoDataAPIConfig {
  appId: string;
  apiKey: string;
  cluster: string;
  database: string;
  collection: string;
}

interface MongoLatestData {
  timestamp: string;
  total_students: number;
  phase_distribution: Record<string, number>;
  model_phase_distribution?: Record<string, number>;
  red_zone_overrides?: number;
  ml_model_used?: string;
  preview?: any[];
  output_path?: string;
}

/**
 * Get MongoDB Data API configuration from environment variables
 */
function getMongoConfig(): MongoDataAPIConfig {
  const appId = import.meta.env.VITE_MONGO_APP_ID;
  const apiKey = import.meta.env.VITE_MONGO_API_KEY;
  const cluster = import.meta.env.VITE_MONGO_CLUSTER || 'Cluster0';
  const database = import.meta.env.VITE_MONGO_DB || 'dropout_prediction';
  const collection = import.meta.env.VITE_MONGO_COLLECTION || 'data';

  if (!appId || !apiKey) {
    throw new Error('MongoDB Data API credentials not configured. Please set VITE_MONGO_APP_ID and VITE_MONGO_API_KEY in .env file.');
  }

  return { appId, apiKey, cluster, database, collection };
}

/**
 * Fetch the latest data from MongoDB using the Data API
 * 
 * @returns Promise with the latest cached data
 * @throws Error if fetch fails or data is not found
 */
export const fetchMongoData = async (): Promise<MongoLatestData | null> => {
  try {
    const config = getMongoConfig();
    
    const url = `https://data.mongodb-api.com/app/${config.appId}/endpoint/data/v1/action/findOne`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-key': config.apiKey,
      },
      body: JSON.stringify({
        collection: config.collection,
        database: config.database,
        dataSource: config.cluster,
        filter: { _id: 'latest' },
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('MongoDB Data API error:', errorText);
      throw new Error(`MongoDB Data API request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    if (!data.document) {
      console.warn('No document found in MongoDB. Backend may not have run yet.');
      return null;
    }

    return data.document as MongoLatestData;
  } catch (error) {
    console.error('Failed to fetch data from MongoDB:', error);
    throw error;
  }
};

/**
 * Check if MongoDB Data API is configured
 * 
 * @returns true if credentials are available
 */
export const isMongoConfigured = (): boolean => {
  try {
    getMongoConfig();
    return true;
  } catch {
    return false;
  }
};

/**
 * Fetch data with automatic retry logic
 * 
 * @param maxRetries Maximum number of retry attempts
 * @param retryDelay Delay between retries in milliseconds
 * @returns Promise with the latest data or null
 */
export const fetchMongoDataWithRetry = async (
  maxRetries = 3,
  retryDelay = 1000
): Promise<MongoLatestData | null> => {
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const data = await fetchMongoData();
      return data;
    } catch (error) {
      lastError = error as Error;
      console.warn(`Attempt ${attempt}/${maxRetries} failed:`, error);
      
      if (attempt < maxRetries) {
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
      }
    }
  }
  
  console.error('All retry attempts failed:', lastError);
  return null;
};

export default {
  fetchMongoData,
  fetchMongoDataWithRetry,
  isMongoConfigured,
};
