import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Cases API
export const casesAPI = {
  submitCase: (caseData) => api.post('/cases/submit_case', caseData),
  getCases: (params) => api.get('/cases/', { params }),
  getCase: (caseId) => api.get(`/cases/${caseId}`),
  resolveCase: (caseId, resolutionTime) => api.put(`/cases/${caseId}/resolve`, { resolution_time: resolutionTime }),
};

// Advisors API
export const advisorsAPI = {
  getAdvisors: (params) => api.get('/advisors/', { params }),
  getAdvisor: (advisorId) => api.get(`/advisors/${advisorId}`),
  getAdvisorDashboard: (advisorId) => api.get(`/advisors/dashboard/${advisorId}`),
  getLearningCurve: (advisorId) => api.get(`/advisors/${advisorId}/learning-curve`),
  updateProfile: (advisorId) => api.post(`/advisors/${advisorId}/update-profile`),
};

// Assignments API
export const assignmentsAPI = {
  acceptCase: (caseId, advisorId) => api.post(`/assignments/case/${caseId}/accept`, { advisor_id: advisorId }),
  declineCase: (caseId, advisorId, reason) => api.post(`/assignments/case/${caseId}/decline`, { 
    advisor_id: advisorId, 
    action: 'decline', 
    reason 
  }),
  getCaseAssignments: (caseId) => api.get(`/assignments/case/${caseId}`),
};

export default api;
