/**
 * Tools API Client
 *
 * Provides typed API methods for tool operations:
 * - Tax Calculator
 * - Character Counter
 * - Email Templates
 * - Tool listing
 */

import { apiClient, isSuccess } from "./client";
import type {
  ApiResponse,
  EmailTemplate,
  Category,
  UsageHistoryEntry,
} from "@/types";

// ==================== Types ====================

export interface TaxCalculatorRequest {
  calculator_type: "us" | "canada" | "vat";
  items: Array<{
    price: number;
    tax_rate?: number;
  }>;
  discounts?: Array<{
    amount: number;
    type: "fixed" | "percentage";
  }>;
  shipping_cost?: number;
  shipping_taxable?: boolean;
  shipping_tax_rate?: number;
  // Canada specific
  gst_rate?: number;
  pst_rate?: number;
  // VAT specific
  vat_rate?: number;
  // Options
  options?: {
    is_sales_before_tax?: boolean;
    discount_is_taxable?: boolean;
  };
}

/**
 * Shape returned by Tools/tax_calculator.py. US/Canada calculations return
 * the total_* fields; VAT calculations return the *_amount / vat_* fields.
 */
export interface TaxCalculatorResponse {
  item_total: number;
  discount_total: number;
  shipping_cost: number;
  // US / Canada
  shipping_tax?: number;
  total_tax?: number;
  total_amount?: number;
  tax_breakdown?: Array<{ item: string; tax: number }>;
  // VAT
  net_amount?: number;
  vat_amount?: number;
  gross_amount?: number;
  vat_rate_applied?: number;
  vat_breakdown?: Array<{ item: string; net_amount: number; vat: number }>;
}

export interface CharacterCountRequest {
  text: string;
  char_limit?: number;
}

export interface CharacterCountResponse {
  total_characters: number;
  char_limit: number;
  excess_characters: number;
  excess_message: string;
}

export interface ToolCategoryInfo {
  id: number;
  name: string | null;
  slug: string | null;
  color: string | null;
  icon: string | null;
}

export interface RequiredPlanInfo {
  id: number;
  name: string | null;
  tier_level: number | null;
}

export interface ToolInfo {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  route: string | null;
  is_default: boolean;
  is_active: boolean;
  icon: string | null;
  category: ToolCategoryInfo | null;
  is_paid: boolean;
  required_plan: RequiredPlanInfo | null;
  hasAccess: boolean;
}

export interface ToolsListResponse {
  tools: ToolInfo[];
}

export interface CategoriesResponse {
  categories: Category[];
}

export interface FavoritesResponse {
  favorites: number[];
}

export interface UsageHistoryResponse {
  history: UsageHistoryEntry[];
  total: number;
  limit: number;
  offset: number;
}

export interface EmailTemplatesResponse {
  templates: EmailTemplate[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// ==================== API Methods ====================

/**
 * Tools API client with typed methods
 */
export const toolsApi = {
  /**
   * List all available tools with access flags
   */
  async listTools(includeInactive = false): Promise<ApiResponse<ToolsListResponse>> {
    return apiClient.get<ToolsListResponse>("/tools", {
      params: { include_inactive: includeInactive },
    });
  },

  /**
   * List all active tool categories (for filter pills)
   */
  async getCategories(): Promise<ApiResponse<CategoriesResponse>> {
    return apiClient.get<CategoriesResponse>("/tools/categories");
  },

  /**
   * Get the current user's favorited tool IDs
   */
  async getFavorites(): Promise<ApiResponse<FavoritesResponse>> {
    return apiClient.get<FavoritesResponse>("/user/favorites");
  },

  /**
   * Add a tool to the user's favorites
   */
  async addFavorite(toolId: number): Promise<ApiResponse<{ message: string }>> {
    return apiClient.post<{ message: string }>(`/user/favorites/${toolId}`);
  },

  /**
   * Remove a tool from the user's favorites
   */
  async removeFavorite(toolId: number): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/user/favorites/${toolId}`);
  },

  /**
   * Get the user's recent tool usage entries (newest first)
   */
  async getUsageHistory(
    limit = 10,
    offset = 0
  ): Promise<ApiResponse<UsageHistoryResponse>> {
    return apiClient.get<UsageHistoryResponse>("/user/usage-history", {
      params: { limit, offset },
    });
  },

  /**
   * Record a usage event for a client-side tool (e.g. Unix Timestamp).
   * Server-executed tools log automatically. Fire-and-forget: ignore failures.
   */
  async logUsage(toolName: string): Promise<ApiResponse<{ logged: boolean }>> {
    return apiClient.post<{ logged: boolean }>("/tools/usage", {
      tool_name: toolName,
    });
  },

  /**
   * Calculate tax using the backend tax calculator
   */
  async calculateTax(data: TaxCalculatorRequest): Promise<ApiResponse<TaxCalculatorResponse>> {
    return apiClient.post<TaxCalculatorResponse>("/tools/tax-calculator", data);
  },

  /**
   * Count characters in text (optional - can be done client-side)
   */
  async countCharacters(data: CharacterCountRequest): Promise<ApiResponse<CharacterCountResponse>> {
    return apiClient.post<CharacterCountResponse>("/tools/character-counter", data);
  },

  /**
   * List user's email templates
   */
  async listEmailTemplates(params?: {
    page?: number;
    per_page?: number;
    search?: string;
  }): Promise<ApiResponse<EmailTemplatesResponse>> {
    return apiClient.get<EmailTemplatesResponse>("/tools/email-templates", {
      params: params as Record<string, string | number | boolean>,
    });
  },

  /**
   * Create a new email template
   */
  async createEmailTemplate(data: {
    title: string;
    content: string;
  }): Promise<ApiResponse<EmailTemplate>> {
    return apiClient.post<EmailTemplate>("/tools/email-templates", data);
  },

  /**
   * Update an email template
   */
  async updateEmailTemplate(
    id: number,
    data: { title: string; content: string }
  ): Promise<ApiResponse<EmailTemplate>> {
    return apiClient.put<EmailTemplate>(`/tools/email-templates/${id}`, data);
  },

  /**
   * Delete an email template
   */
  async deleteEmailTemplate(id: number): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/tools/email-templates/${id}`);
  },
};

export { isSuccess };
export default toolsApi;
