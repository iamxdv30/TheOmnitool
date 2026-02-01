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
import type { ApiResponse, TaxCalculatorResult, EmailTemplate } from "@/types";

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

export interface TaxCalculatorResponse {
  subtotal: number;
  discount_total: number;
  taxable_amount: number;
  tax_amount: number;
  shipping_cost: number;
  shipping_tax: number;
  total: number;
  items: Array<{
    price: number;
    tax_rate: number;
    tax_amount: number;
    total: number;
  }>;
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

export interface ToolInfo {
  id: number;
  name: string;
  description: string | null;
  route: string | null;
  is_default: boolean;
  hasAccess: boolean;
}

export interface ToolsListResponse {
  tools: ToolInfo[];
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
    return apiClient.get<ToolsListResponse>("/tools/", {
      params: { include_inactive: includeInactive },
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
