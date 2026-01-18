import { z } from "zod";

/**
 * Tax calculator item schema
 */
export const taxItemSchema = z.object({
  price: z.number().min(0, "Price must be positive"),
  taxRate: z.number().min(0).max(100).optional(),
});

/**
 * Tax calculator discount schema
 */
export const taxDiscountSchema = z.object({
  type: z.enum(["percentage", "fixed"]),
  value: z.number().min(0, "Discount must be positive"),
});

/**
 * US Tax Calculator schema
 */
export const usTaxCalculatorSchema = z.object({
  items: z.array(taxItemSchema).min(1, "At least one item is required"),
  discounts: z.array(taxDiscountSchema).optional().default([]),
  shippingCost: z.number().min(0).optional().default(0),
  shippingTaxable: z.boolean().optional().default(false),
  shippingTaxRate: z.number().min(0).max(100).optional(),
  isSalesBeforeTax: z.boolean().optional().default(false),
  discountIsTaxable: z.boolean().optional().default(true),
});

export type USTaxCalculatorFormData = z.infer<typeof usTaxCalculatorSchema>;

/**
 * Canada Tax Calculator schema
 */
export const canadaTaxCalculatorSchema = usTaxCalculatorSchema.extend({
  province: z.string().min(1, "Province is required"),
  gstRate: z.number().min(0).max(100),
  pstRate: z.number().min(0).max(100).optional().default(0),
});

export type CanadaTaxCalculatorFormData = z.infer<typeof canadaTaxCalculatorSchema>;

/**
 * VAT Calculator schema
 */
export const vatCalculatorSchema = usTaxCalculatorSchema.extend({
  vatRate: z.number().min(0).max(100),
});

export type VATCalculatorFormData = z.infer<typeof vatCalculatorSchema>;

/**
 * Character counter schema
 */
export const charCounterSchema = z.object({
  text: z.string(),
  charLimit: z.number().min(1).optional().default(3532),
});

export type CharCounterFormData = z.infer<typeof charCounterSchema>;

/**
 * Email template schema
 */
export const emailTemplateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be less than 200 characters"),
  content: z
    .string()
    .min(1, "Content is required")
    .max(10000, "Content must be less than 10,000 characters"),
});

export type EmailTemplateFormData = z.infer<typeof emailTemplateSchema>;

/**
 * Contact form schema
 */
export const contactSchema = z.object({
  name: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be less than 100 characters"),
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  queryType: z.enum(["general", "bug", "suggestion"], {
    message: "Please select a query type",
  }),
  message: z
    .string()
    .min(10, "Message must be at least 10 characters")
    .max(5000, "Message must be less than 5,000 characters"),
});

export type ContactFormData = z.infer<typeof contactSchema>;
