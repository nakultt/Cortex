/**
 * Application Configuration
 * 
 * Update these values when using this project as a template.
 * This centralizes all branding and app-specific configuration.
 */

export const APP_CONFIG = {
  // Application Name
  name: '{{APP_NAME}}',
  
  // Branding
  logo: '/{{APP_LOGO}}.png',
  
  // Version & Copyright
  version: '1.0.0',
  copyright: '© 2026 {{APP_NAME}}. All rights reserved.',
  
  // Local Storage Keys
  storageKeys: {
    user: '{{APP_NAME}}_user',
    remember: '{{APP_NAME}}_remember'
  },
  
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000'
  },
  
  // Development Settings
  dev: {
    // Set to true to bypass login screen (useful for development/demos)
    bypassLogin: true
  }
} as const;
