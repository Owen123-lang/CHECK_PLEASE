// API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
export const AI_API_BASE_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // User endpoints
  LOGIN: `${API_BASE_URL}/api/users/login`,
  REGISTER: `${API_BASE_URL}/api/users/register`,
  USER: (email: string) => `${API_BASE_URL}/api/users/${email}`,
  
  // Notebook endpoints
  NOTEBOOKS: `${API_BASE_URL}/api/notebooks`,
  NOTEBOOK: (id: string | number) => `${API_BASE_URL}/api/notebooks/${id}`,
  
  // Chat endpoints
  CHAT: `${API_BASE_URL}/api/chat`,
  CHAT_SESSION: (sessionId: string) => `${API_BASE_URL}/api/chat/${sessionId}`,
  CHAT_NOTEBOOK: (notebookId: string) => `${API_BASE_URL}/api/chat/notebook/${notebookId}`,
  
  // AI endpoints
  AI_CHAT: `${AI_API_BASE_URL}/api/chat`,
  AI_GENERATE_CV: `${AI_API_BASE_URL}/api/generate-cv`,
  AI_UPLOAD_PDF: `${AI_API_BASE_URL}/api/upload-pdf`,
  
  // PDF endpoints
  PDF: `${API_BASE_URL}/api/pdf`,
  PDF_UPLOAD: `${API_BASE_URL}/api/pdf/upload`,
};