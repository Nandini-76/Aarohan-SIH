/**
 * Service to keep Render backend alive by pinging it periodically
 * This prevents the free tier from going inactive due to inactivity
 */

const RENDER_BACKEND_URL = 'https://arohann.onrender.com';
const PING_INTERVAL = 2 * 60 * 1000; // 2 minutes in milliseconds
const PING_ENDPOINT = '/health'; // Health check endpoint
const PING_TIMEOUT = 60000; // 60 seconds timeout for backend warmup

class RenderPingService {
  private intervalId: NodeJS.Timeout | null = null;
  private isActive = false;

  /**
   * Start pinging the Render backend every 2 minutes
   */
  start(): void {
    if (this.isActive) {
      console.log('🏓 Render ping service already active');
      return;
    }

    console.log('🚀 Starting Render ping service - pinging every 2 minutes');
    
    // Ping immediately on start
    this.ping();
    
    // Set up interval for regular pings
    this.intervalId = setInterval(() => {
      this.ping();
    }, PING_INTERVAL);
    
    this.isActive = true;
  }

  /**
   * Stop pinging the Render backend
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isActive = false;
    console.log('⏹️ Render ping service stopped');
  }

  /**
   * Send a ping to the Render backend
   */
  private async ping(): Promise<void> {
    const startTime = Date.now();
    
    try {
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), PING_TIMEOUT);
      
      // Use fetch for a lightweight ping
      const response = await fetch(`${RENDER_BACKEND_URL}${PING_ENDPOINT}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const duration = Date.now() - startTime;
      
      if (response.ok) {
        console.log(`🏓 Render ping successful (${duration}ms) - ${new Date().toLocaleTimeString()}`);
      } else {
        console.warn(`⚠️ Render ping returned ${response.status} - ${new Date().toLocaleTimeString()}`);
      }
    } catch (error) {
      const duration = Date.now() - startTime;
      if (error instanceof Error && error.name === 'AbortError') {
        console.error(`❌ Render ping timeout (${duration}ms) - ${new Date().toLocaleTimeString()}`);
      } else {
        console.error(`❌ Render ping failed (${duration}ms) - ${new Date().toLocaleTimeString()}:`, error);
      }
      // Don't throw - we want to keep trying
    }
  }

  /**
   * Get current status
   */
  getStatus(): { isActive: boolean; interval: number } {
    return {
      isActive: this.isActive,
      interval: PING_INTERVAL,
    };
  }
}

// Create singleton instance
export const renderPingService = new RenderPingService();

// Auto-start in production environment
if (import.meta.env.PROD) {
  // Small delay to ensure app is fully loaded
  setTimeout(() => {
    renderPingService.start();
  }, 5000); // 5 second delay
}

export default renderPingService;