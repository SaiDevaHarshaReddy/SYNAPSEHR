import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import type { ApiResponse, User, TokenResponse, Employee, Department, LeaveType, LeaveBalance, LeaveRequest, Notification, ChatResponse, Conversation, Message, Document, Workflow, DashboardMetrics, PaginatedResponse, PaginationParams } from '../types';

export const API_BASE_URL = import.meta.env.PUBLIC_API_URL || "https://synapsehr-6qwi.onrender.com";
console.log("API_BASE_URL =", API_BASE_URL);

class ApiService {
  private client: AxiosInstance;
  private cache = new Map<string, { data: any; expiry: number }>();
  private CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  private clearCache() {
    this.cache.clear();
  }

  private async _get<T>(url: string, config?: any): Promise<{ data: T }> {
    const cacheKey = url + JSON.stringify(config?.params || {});
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() < cached.expiry) {
      return { data: cached.data as T };
    }
    const response = await this.client.get<T>(url, config);
    this.cache.set(cacheKey, { data: response.data, expiry: Date.now() + this.CACHE_TTL });
    return response;
  }

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      if (typeof window !== 'undefined') {
        const token = sessionStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    });

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          if (typeof window !== 'undefined') {
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(email: string, password: string): Promise<TokenResponse> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<TokenResponse>>('/api/v1/auth/login', { email, password });
    return response.data.data!;
  }

  async register(full_name: string, email: string, password: string): Promise<TokenResponse> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<TokenResponse>>('/api/v1/auth/register', { full_name, email, password });
    return response.data.data!;
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<TokenResponse>>('/api/v1/auth/refresh', { refresh_token: refreshToken });
    return response.data.data!;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this._get<ApiResponse<User>>('/api/v1/auth/me');
    return response.data.data!;
  }

  // Employees
  async getEmployees(params?: PaginationParams): Promise<PaginatedResponse<Employee>> {
    const response = await this._get<PaginatedResponse<Employee>>('/api/v1/employees', { params });
    return response.data;
  }

  async getEmployee(id: string): Promise<Employee> {
    const response = await this._get<ApiResponse<Employee>>(`/api/v1/employees/${id}`);
    return response.data.data!;
  }

  async createEmployee(data: Partial<Employee>): Promise<Employee> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<Employee>>('/api/v1/employees', data);
    return response.data.data!;
  }

  async updateEmployee(id: string, data: Partial<Employee>): Promise<Employee> {
    this.clearCache();
    const response = await this.client.patch<ApiResponse<Employee>>(`/api/v1/employees/${id}`, data);
    return response.data.data!;
  }

  async deleteEmployee(id: string): Promise<void> {
    this.clearCache();
    await this.client.delete(`/api/v1/employees/${id}`);
  }

  // Departments
  async getDepartments(params?: PaginationParams): Promise<PaginatedResponse<Department>> {
    const response = await this._get<PaginatedResponse<Department>>('/api/v1/departments', { params });
    return response.data;
  }

  async getDepartment(id: string): Promise<Department> {
    const response = await this._get<ApiResponse<Department>>(`/api/v1/departments/${id}`);
    return response.data.data!;
  }

  // Leave
  async getLeaveTypes(): Promise<LeaveType[]> {
    const response = await this._get<ApiResponse<LeaveType[]>>('/api/v1/leave/types');
    return response.data.data!;
  }

  async getLeaveBalance(): Promise<LeaveBalance[]> {
    const response = await this._get<ApiResponse<LeaveBalance[]>>('/api/v1/leave/balance');
    return response.data.data!;
  }

  async getLeaveHistory(): Promise<LeaveRequest[]> {
    const response = await this._get<ApiResponse<LeaveRequest[]>>('/api/v1/leave/history');
    return response.data.data!;
  }

  async createLeaveRequest(data: { leave_type_id: string; start_date: string; end_date: string; reason?: string }): Promise<LeaveRequest> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<LeaveRequest>>('/api/v1/leave/request', data);
    return response.data.data!;
  }

  async approveLeave(requestId: string, status: string): Promise<LeaveRequest> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<LeaveRequest>>(`/api/v1/leave/${requestId}/approve?status=${status}`);
    return response.data.data!;
  }

  async markLeaveAsRead(requestId: string, isRead: boolean = true): Promise<LeaveRequest> {
    this.clearCache();
    const response = await this.client.patch<ApiResponse<LeaveRequest>>(`/api/v1/leave/${requestId}/read?is_read=${isRead}`);
    return response.data.data!;
  }

  // Chat
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<ChatResponse>>('/api/v1/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data.data!;
  }

  async getChatHistory(): Promise<Conversation[]> {
    const response = await this._get<ApiResponse<Conversation[]>>('/api/v1/chat/history');
    return response.data.data!;
  }

  async getConversation(id: string): Promise<Conversation & { messages: Message[] }> {
    const response = await this._get<ApiResponse<Conversation & { messages: Message[] }>>(`/api/v1/chat/${id}`);
    return response.data.data!;
  }

  // Notifications
  async getNotifications(): Promise<Notification[]> {
    const response = await this._get<ApiResponse<Notification[]>>('/api/v1/notifications');
    return response.data.data!;
  }

  async getUnreadCount(): Promise<number> {
    const response = await this._get<ApiResponse<{ count: number }>>('/api/v1/notifications/unread-count');
    return response.data.data?.count || 0;
  }

  async markNotificationAsRead(id: string): Promise<Notification> {
    this.clearCache();
    const response = await this.client.patch<ApiResponse<Notification>>(`/api/v1/notifications/${id}/read`);
    return response.data.data!;
  }

  // Documents
  async generateDocument(data: { employee_id: string; document_type: string }): Promise<Document> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<Document>>('/api/v1/documents/generate', data);
    return response.data.data!;
  }

  async getDocuments(): Promise<Document[]> {
    const response = await this._get<ApiResponse<Document[]>>('/api/v1/documents');
    return response.data.data!;
  }

  async downloadDocument(id: string): Promise<Blob> {
    const response = await this._get<Blob>(`/api/v1/documents/${id}`, { responseType: 'blob' });
    return response.data;
  }

  // Analytics
  async getDashboardMetrics(filters?: { start_date?: string; end_date?: string; department_id?: string }): Promise<DashboardMetrics> {
    const params = new URLSearchParams(filters as any).toString();
    const response = await this._get<ApiResponse<DashboardMetrics>>(`/api/v1/analytics/dashboard${params ? '?' + params : ''}`);
    return response.data.data!;
  }

  async getLeaveAnalytics(filters?: { start_date?: string; end_date?: string; department_id?: string }): Promise<Record<string, number>> {
    const params = new URLSearchParams(filters as any).toString();
    const response = await this._get<ApiResponse<Record<string, number>>>(`/api/v1/analytics/leave${params ? '?' + params : ''}`);
    return response.data.data!;
  }

  async getDepartmentDistribution(filters?: { start_date?: string; end_date?: string; department_id?: string }): Promise<Array<{ department: string; count: number }>> {
    const params = new URLSearchParams(filters as any).toString();
    const response = await this._get<ApiResponse<Array<{ department: string; count: number }>>>(`/api/v1/analytics/departments${params ? '?' + params : ''}`);
    return response.data.data!;
  }

  // Workflows
  async getWorkflows(): Promise<Workflow[]> {
    const response = await this._get<ApiResponse<Workflow[]>>('/api/v1/workflows');
    return response.data.data!;
  }

  async getWorkflow(id: string): Promise<Workflow> {
    const response = await this._get<ApiResponse<Workflow>>(`/api/v1/workflows/${id}`);
    return response.data.data!;
  }

  // Knowledge Base
  async uploadKnowledge(file: File, title: string, category: string, department?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('category', category);
    if (department) formData.append('department', department);

    this.clearCache();
    const response = await this.postForm('/api/v1/knowledge/upload', formData);
    return response.data || response;
  }

  async listKnowledgeDocuments(): Promise<any[]> {
    const response = await this._get<ApiResponse<any[]>>('/api/v1/knowledge');
    return response.data.data!;
  }

  async deleteKnowledgeDocument(id: string): Promise<void> {
    this.clearCache();
    await this.client.delete(`/api/v1/knowledge/${id}`);
  }

  async getKnowledgeStats(): Promise<any> {
    const response = await this._get<ApiResponse<any>>('/api/v1/knowledge/stats');
    return response.data.data!;
  }

  // Policies
  async getPolicies(): Promise<any[]> {
    const response = await this._get<ApiResponse<any[]>>('/api/v1/policies');
    return response.data.data!;
  }

  async getPolicy(id: string): Promise<any> {
    const response = await this._get<ApiResponse<any>>(`/api/v1/policies/${id}`);
    return response.data.data!;
  }

  async deletePolicy(id: string): Promise<void> {
    this.clearCache();
    await this.client.delete(`/api/v1/policies/${id}`);
  }

  // Auth
  async logout(): Promise<void> {
    await this.client.post('/api/v1/auth/logout');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  }

  async forgotPassword(email: string): Promise<void> {
    await this.client.post('/api/v1/auth/forgot-password', { email });
  }

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await this.client.post('/api/v1/auth/reset-password', { token, new_password: newPassword });
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.client.post('/api/v1/auth/change-password', { current_password: currentPassword, new_password: newPassword });
  }

  // Admin
  async getAuditLogs(): Promise<any[]> {
    const response = await this._get<ApiResponse<any[]>>('/api/v1/admin/audit');
    return response.data.data!;
  }

  async getRoles(): Promise<any[]> {
    const response = await this._get<ApiResponse<any[]>>('/api/v1/admin/roles');
    return response.data.data!;
  }

  async getAIDashboard(): Promise<any> {
    const response = await this._get<ApiResponse<any>>('/api/v1/analytics/ai');
    return response.data.data!;
  }

  // Generic helpers for untyped endpoints
  async post(url: string, data: any, config?: any): Promise<any> {
    this.clearCache();
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  async get(url: string): Promise<any> {
    const response = await this._get(url);
    return response.data;
  }

  async patch(url: string, data: any): Promise<any> {
    this.clearCache();
    const response = await this.client.patch(url, data);
    return response.data;
  }

  async postForm(url: string, formData: FormData): Promise<any> {
    this.clearCache();
    let token = '';
    if (typeof window !== 'undefined') {
      token = sessionStorage.getItem('access_token') || '';
    }
    const response = await axios.post(`${API_BASE_URL}${url}`, formData, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    return response.data;
  }

  async getRecruitmentStats(filters?: { start_date?: string; end_date?: string }): Promise<any> {
    const params = new URLSearchParams(filters as any).toString();
    const response = await this._get<ApiResponse<any>>(`/api/v1/recruitment/stats${params ? '?' + params : ''}`);
    return response.data.data!;
  }

  // HR Tickets
  async getHRTickets(): Promise<any[]> {
    const response = await this._get<ApiResponse<any[]>>('/api/v1/hr-tickets');
    return response.data.data!;
  }

  async createHRTicket(subject: string, message: string): Promise<any> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<any>>('/api/v1/hr-tickets', { subject, message });
    return response.data.data!;
  }

  async replyToHRTicket(ticketId: string, message: string): Promise<any> {
    this.clearCache();
    const response = await this.client.post<ApiResponse<any>>(`/api/v1/hr-tickets/${ticketId}/reply`, { message });
    return response.data.data!;
  }

  async delete(url: string): Promise<void> {
    this.clearCache();
    await this.client.delete(url);
  }
}

export const api = new ApiService();
export default api;
