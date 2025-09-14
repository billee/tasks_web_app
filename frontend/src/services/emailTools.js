import api from './api';

export const emailToolsChat = async (messages, toolType = 'email') => {
  const response = await api.post('/email-tools/chat', {
    messages,
    tool_type: toolType
  });
  return response.data;
};

export const getAvailableTools = async () => {
  const response = await api.get('/email-tools/tools/available');
  return response.data;
};