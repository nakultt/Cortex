/**
 * Application Configuration
 * 
 * Cortex - AI-powered Knowledge Assistant
 */

export const APP_CONFIG = {
  // Application Name
  name: 'Cortex',
  
  // Branding
  logo: '/logo.png',
  
  // Version & Copyright
  version: '1.0.0',
  copyright: '© 2026 Cortex. All rights reserved.',
  
  // Local Storage Keys
  storageKeys: {
    user: 'cortex_user',
    remember: 'cortex_remember'
  },
  
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000'
  },
  
  // Development Settings
  dev: {
    // Set to true to bypass login screen (useful for development/demos)
    bypassLogin: false
  }
} as const;
