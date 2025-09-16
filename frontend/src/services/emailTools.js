import api from './api';

export const emailToolsChat = async (messages, toolType = 'email') => {
  try {
    const response = await api.post('/email-tools/chat', {
      messages,
      tool_type: toolType
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      // Don't automatically logout, let the component handle it
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const getAvailableTools = async () => {
  const response = await api.get('/email-tools/tools/available');
  return response.data;
};

export const getEmailHistory = async () => {
    const response = await api.get('/email-tools/history');
    return response;
};

export const getAdminEmailHistory = async () => {
    const response = await api.get('/email-tools/admin/history');
    return response;
};

export const approveAndSendEmail = async (emailData) => {
  const response = await api.post('/email-tools/approve-and-send', emailData);
  return response.data;
};

export const saveEmailDraft = async (emailData) => {
  const response = await api.post('/email-tools/save-draft', emailData);
  return response.data;
};

export const cancelEmailComposition = async (compositionId) => {
  const response = await api.delete(`/email-tools/cancel-composition/${compositionId}`);
  return response.data;
};