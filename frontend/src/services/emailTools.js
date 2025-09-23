import api from './api';

export const emailToolsChat = async (messages, toolType = 'email') => {
  try {
    const formattedMessages = messages.map(msg => ({
      text: msg.text,
      isUser: msg.isUser,
      time: msg.time || new Date().toISOString()
    }));

    const response = await api.post('/email-tools/chat', {
      messages: formattedMessages,
      tool_type: toolType,
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
  try {
    const response = await api.get('/email-tools/tools/available');
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const getEmailHistory = async () => {
  try {
    const response = await api.get('/email-tools/history');
    return response;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const getAdminEmailHistory = async () => {
  try {
    const response = await api.get('/email-tools/admin/history');
    return response;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const approveAndSendEmail = async (emailData) => {
  try {
  const response = await api.post('/email-tools/approve-and-send', emailData);
  return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const saveEmailDraft = async (emailData) => {
  try {
  const response = await api.post('/email-tools/save-draft', emailData);
  return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const cancelEmailComposition = async (compositionId) => {
  try {
  const response = await api.delete(`/email-tools/cancel-composition/${compositionId}`);
  return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const getEmailContent = async (emailId) => {
  try {
  const response = await api.get(`/email-tools/email-content/${emailId}`);
  return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};

export const readGmailInbox = async (maxResults = 10) => {
  try {
    const response = await api.post('/read-gmail-tool/read-inbox', {
      max_results: maxResults
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please login again');
    }
    throw error;
  }
};