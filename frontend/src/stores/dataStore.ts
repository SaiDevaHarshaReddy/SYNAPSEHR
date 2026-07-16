import { atom } from 'nanostores';
import { api } from '../services/api';
import type { Employee, Department, LeaveRequest, Document } from '../types';

export const employeesStore = atom<Employee[]>([]);
export const departmentsStore = atom<Department[]>([]);
export const leaveRequestsStore = atom<LeaveRequest[]>([]);
export const knowledgeStore = atom<any[]>([]);
export const candidatesStore = atom<any[]>([]); // Using any since Candidate might not be in types yet
export const dashboardMetricsStore = atom<any>(null);
export const recruitmentStatsStore = atom<any>(null);
export const deptDistributionStore = atom<any>(null);
export const leaveAnalyticsStore = atom<any>(null);
export const aiInsightsStore = atom<any>(null);

export const dataStoreStatus = atom<{
  isLoading: boolean;
  hasLoaded: boolean;
}>({ isLoading: false, hasLoaded: false });

export async function preloadData() {
  if (dataStoreStatus.get().isLoading || dataStoreStatus.get().hasLoaded) return;
  
  dataStoreStatus.set({ isLoading: true, hasLoaded: false });
  
  try {
    const promises = [
      api.getDepartments({ page: 1, limit: 100 }),
      api.getEmployees({ page: 1, limit: 100 }),
      api.getLeaveHistory().catch(() => []), 
      api.listKnowledgeDocuments().catch(() => []),
      api.get('/api/v1/recruitment/candidates').catch(() => []),
      api.getDashboardMetrics().catch(() => null),
      api.get('/api/v1/recruitment/stats').catch(() => null),
      api.getDepartmentDistribution().catch(() => []),
      api.getLeaveAnalytics().catch(() => null),
      api.get('/api/v1/analytics/insights').catch(() => null)
    ];

    const [depsRes, empsRes, leaves, knowledge, candidatesRes, dashMetrics, recStats, deptDist, leaveAnalyt, aiInsights] = await Promise.allSettled(promises);

    if (depsRes.status === 'fulfilled') {
      departmentsStore.set((depsRes.value as any)?.data || []);
    }
    if (empsRes.status === 'fulfilled') {
      employeesStore.set((empsRes.value as any)?.data || []);
    }
    if (leaves.status === 'fulfilled') {
      leaveRequestsStore.set((leaves.value as any) || []);
    }
    if (knowledge.status === 'fulfilled') {
      knowledgeStore.set((knowledge.value as any) || []);
    }
    if (candidatesRes.status === 'fulfilled') {
      const data = (candidatesRes.value as any)?.data || (candidatesRes.value as any) || [];
      candidatesStore.set(data);
    }
    if (dashMetrics.status === 'fulfilled' && dashMetrics.value) {
      dashboardMetricsStore.set(dashMetrics.value);
    }
    if (recStats.status === 'fulfilled' && recStats.value) {
      recruitmentStatsStore.set((recStats.value as any)?.data || recStats.value);
    }
    if (deptDist.status === 'fulfilled' && deptDist.value) {
      deptDistributionStore.set(deptDist.value);
    }
    if (leaveAnalyt.status === 'fulfilled' && leaveAnalyt.value) {
      leaveAnalyticsStore.set(leaveAnalyt.value);
    }
    if (aiInsights.status === 'fulfilled' && aiInsights.value) {
      aiInsightsStore.set((aiInsights.value as any)?.data || aiInsights.value);
    }
    
    dataStoreStatus.set({ isLoading: false, hasLoaded: true });
  } catch (error) {
    console.error('Failed to preload application data:', error);
    dataStoreStatus.set({ isLoading: false, hasLoaded: false });
  }
}
