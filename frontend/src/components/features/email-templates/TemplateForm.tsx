"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { emailTemplateSchema, type EmailTemplateFormData } from "@/lib/validations";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/forms";
import { Textarea } from "@/components/forms/Textarea";
import { Label } from "@/components/ui/Label";
import { Controller } from "react-hook-form";
import { Save, X, Loader2 } from "lucide-react";

interface TemplateFormProps {
  initialData?: { title: string; content: string };
  onSubmit: (data: EmailTemplateFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  submitLabel?: string;
}

export function TemplateForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  submitLabel = "Save Template",
}: TemplateFormProps) {
  const form = useForm<EmailTemplateFormData>({
    resolver: zodResolver(emailTemplateSchema),
    defaultValues: {
      title: initialData?.title || "",
      content: initialData?.content || "",
    },
  });

  const handleSubmit = async (data: EmailTemplateFormData) => {
    await onSubmit(data);
    if (!initialData) {
      form.reset();
    }
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
      <FormField
        name="title"
        control={form.control}
        label="Template Title"
        placeholder="e.g., Welcome Email, Follow-up Template"
        required
      />

      <div className="space-y-2">
        <Label htmlFor="content">
          Template Content <span className="text-danger">*</span>
        </Label>
        <Controller
          name="content"
          control={form.control}
          render={({ field, fieldState: { error } }) => (
            <>
              <Textarea
                id="content"
                placeholder="Enter your email template content here..."
                className="min-h-[200px]"
                error={error?.message}
                {...field}
              />
              {error && (
                <p className="text-xs text-danger" role="alert">
                  {error.message}
                </p>
              )}
            </>
          )}
        />
      </div>

      <div className="flex gap-2">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          {submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel}>
            <X className="mr-2 h-4 w-4" />
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
