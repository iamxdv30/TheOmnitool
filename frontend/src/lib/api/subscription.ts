/**
 * Subscription API Client
 *
 * Read-only subscription operations:
 * - List available plans
 * - Get the current user's subscription
 *
 * Subscribe/cancel operations are deferred until a payment provider is
 * integrated on the backend (dashboard-redesign plan §2F).
 */

import { apiClient, isSuccess } from "./client";
import type { ApiResponse, SubscriptionPlan, UserSubscription } from "@/types";

export interface PlansResponse {
  plans: SubscriptionPlan[];
}

export interface UserSubscriptionResponse {
  subscription: UserSubscription | null;
}

export const subscriptionApi = {
  /**
   * List all active subscription plans (ordered by tier level)
   */
  async getPlans(): Promise<ApiResponse<PlansResponse>> {
    return apiClient.get<PlansResponse>("/tools/plans");
  },

  /**
   * Get the current user's active subscription (null if none)
   */
  async getUserSubscription(): Promise<ApiResponse<UserSubscriptionResponse>> {
    return apiClient.get<UserSubscriptionResponse>("/user/subscription");
  },
};

export { isSuccess };
export default subscriptionApi;
