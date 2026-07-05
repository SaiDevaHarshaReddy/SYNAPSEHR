import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export const employeeSchema = z.object({
  first_name: z.string().min(1, 'First name is required').max(100),
  last_name: z.string().min(1, 'Last name is required').max(100),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  date_of_birth: z.string().optional(),
  gender: z.enum(['male', 'female', 'other']).optional(),
  blood_group: z.string().optional(),
  address: z.string().optional(),
  designation: z.string().optional(),
  department_id: z.string().uuid('Invalid department').optional(),
  employment_type: z.enum(['full_time', 'part_time', 'contract', 'intern']).default('full_time'),
  work_location: z.string().optional(),
  joining_date: z.string().optional(),
});

export const departmentSchema = z.object({
  name: z.string().min(1, 'Department name is required').max(100),
  code: z.string().min(1, 'Department code is required').max(20),
  description: z.string().optional(),
});

export const leaveRequestSchema = z.object({
  leave_type_id: z.string().uuid('Please select a leave type'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  reason: z.string().max(500).optional(),
}).refine(
  (data) => new Date(data.end_date) >= new Date(data.start_date),
  { message: 'End date must be after start date', path: ['end_date'] }
);

export const documentGenerateSchema = z.object({
  employee_id: z.string().uuid('Please select an employee'),
  document_type: z.enum([
    'offer_letter',
    'appointment_letter',
    'experience_letter',
    'salary_certificate',
    'promotion_letter',
    'warning_letter',
    'relieving_letter',
    'termination_letter',
  ], { required_error: 'Please select a document type' }),
  additional_data: z.record(z.any()).optional(),
});

export const knowledgeUploadSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  category: z.string().min(1, 'Category is required'),
  department: z.string().max(100).optional(),
});

export const chatMessageSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty').max(5000),
  conversation_id: z.string().uuid().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type EmployeeFormData = z.infer<typeof employeeSchema>;
export type DepartmentFormData = z.infer<typeof departmentSchema>;
export type LeaveRequestFormData = z.infer<typeof leaveRequestSchema>;
export type DocumentGenerateFormData = z.infer<typeof documentGenerateSchema>;
export type KnowledgeUploadFormData = z.infer<typeof knowledgeUploadSchema>;
export type ChatMessageFormData = z.infer<typeof chatMessageSchema>;
