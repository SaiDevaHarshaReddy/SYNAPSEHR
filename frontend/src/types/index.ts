export interface User {
  user_id: string;
  email: string;
  role: 'employee' | 'manager' | 'hr' | 'administrator';
  organization_id: string;
  organization_name?: string;
  employee_name?: string;
}

export interface Employee {
  id: string;
  user_id: string;
  department_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  designation?: string;
  phone?: string;
  address?: string;
  gender?: string;
  date_of_birth?: string;
  joining_date?: string;
  employment_type: string;
  status: string;
  manager_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Department {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  manager_id?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveType {
  id: string;
  name: string;
  days_per_year: number;
  requires_approval: boolean;
  is_paid: boolean;
}

export interface LeaveBalance {
  id: string;
  leave_type_id: string;
  leave_type_name?: string;
  available_days: number;
  used_days: number;
  carry_forward_days: number;
  year: number;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name?: string;
  leave_type_id: string;
  leave_type_name?: string;
  start_date: string;
  end_date: string;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  is_read?: boolean;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  employee_id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

export interface Conversation {
  id: string;
  employee_id: string;
  title?: string;
  started_at: string;
  ended_at?: string;
  created_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender: 'user' | 'assistant' | 'system';
  message: string;
  token_usage?: number;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  workflow_steps?: Record<string, unknown>[];
  sources_used?: string[];
  execution_time_ms?: number;
}

export interface Workflow {
  id: string;
  employee_id: string;
  workflow_type: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  steps: WorkflowStep[];
  created_at: string;
}

export interface WorkflowStep {
  id: string;
  step_name: string;
  agent_name?: string;
  status: string;
  duration_ms?: number;
  output?: Record<string, unknown>;
  created_at: string;
}

export interface Document {
  id: string;
  employee_id: string;
  document_type: string;
  storage_path: string;
  generated_by?: string;
  generated_at: string;
  created_at: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sort?: string;
  order?: 'asc' | 'desc';
  search?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: {
    code: string;
    message: string;
    request_id?: string;
  };
}

export interface DashboardMetrics {
  total_employees: number;
  pending_approvals: number;
  todays_leave: number;
  total_workflows: number;
  completed_workflows: number;
  workflow_success_rate: number;
}
