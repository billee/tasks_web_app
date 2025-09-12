// src/config/llmConfig.js
const config = {
  // Get values from environment variables
  getApiKey() {
    // First try environment variable
    const envKey = process.env.REACT_APP_OPENAI_API_KEY;
    
    // Debug logging (remove in production)
    console.log('Environment API Key:', envKey ? 'Found' : 'Not found');
    console.log('All REACT_APP env vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));
    
    if (envKey && envKey.trim() !== '') {
      return envKey.trim();
    }
    
    // If no key is found, return null instead of throwing error immediately
    return null;
  },
  
  getModel() {
    const envModel = process.env.REACT_APP_OPENAI_MODEL;
    // Default to gpt-3.5-turbo if not specified
    return envModel && envModel.trim() !== '' ? envModel.trim() : 'gpt-4o-mini';
  }
};

export default config;