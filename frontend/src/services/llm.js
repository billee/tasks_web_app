// src/services/llm.js
import config from '../config/llmConfig';

export const getLLMResponse = async (messages) => {
  try {
    const apiKey = config.getApiKey();
    const model = config.getModel();
    
    console.log('API Key exists:', !!apiKey);
    console.log('Model:', model);

    if (!apiKey || apiKey.trim() === '') {
      throw new Error('OpenAI API key not configured. Please add REACT_APP_OPENAI_API_KEY to your .env file and restart the development server.');
    }

    // Format messages for OpenAI API
    const formattedMessages = messages.map(msg => ({
      role: msg.isUser ? 'user' : 'assistant',
      content: msg.text
    }));

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model,
        messages: formattedMessages,
        max_tokens: 800,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || `API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling OpenAI API:', error);
    throw error;
  }
};
