// User types
export interface User {
  id: number;
  username: string;
  email: string;
  role: "user" | "admin" | "superadmin";
  email_verified: boolean;
  created_at: string;
  fname?: string;
  lname?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  last_login?: string;
}

// API Response types
export interface ApiResponse<T = unknown> {
  status: "success" | "error";
  data?: T;
  message?: string;
  error_code?: string;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
  recaptcha_token?: string;
}

export interface RegisterCredentials {
  name: string;
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Profile types
export interface ProfileData {
  fname?: string;
  lname?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
}

export interface PasswordChangeData {
  currentPassword: string;
  newPassword: string;
  confirmNewPassword: string;
}

// Tool types
export interface Tool {
  id: number;
  name: string;
  display_name: string;
  description: string;
  route: string;
  is_default: boolean;
}

export interface ToolAccess {
  tool_name: string;
  granted_at: string;
}

// Email Template types
export interface EmailTemplate {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

// Tax Calculator types
export interface TaxItem {
  price: number;
  taxRate?: number;
}

export interface TaxDiscount {
  type: "percentage" | "fixed";
  value: number;
}

export interface TaxCalculatorInput {
  calculatorType: "us" | "canada" | "vat";
  items: TaxItem[];
  discounts: TaxDiscount[];
  shippingCost: number;
  shippingTaxable: boolean;
  shippingTaxRate?: number;
  // Canada specific
  province?: string;
  gstRate?: number;
  pstRate?: number;
  // VAT specific
  vatRate?: number;
  // Options
  isSalesBeforeTax: boolean;
  discountIsTaxable: boolean;
}

export interface TaxCalculatorResult {
  itemTotal: number;
  discountTotal: number;
  shippingTotal: number;
  taxBreakdown: {
    name: string;
    rate: number;
    amount: number;
  }[];
  totalTax: number;
  grandTotal: number;
}

// Admin types
export interface AdminUser extends User {
  tools: string[];
}

export interface CreateUserData {
  username: string;
  email: string;
  password: string;
  fname?: string;
  lname?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  role?: "user" | "admin";
}

// Contact types
export interface ContactFormData {
  name: string;
  email: string;
  queryType: "general" | "bug" | "suggestion";
  message: string;
}

// Pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
}
