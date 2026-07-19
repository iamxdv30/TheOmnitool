"use client";

import { type ReactNode } from "react";
import {
  Controller,
  type Control,
  type FieldPath,
  type FieldValues,
} from "react-hook-form";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import { PasswordInput } from "./PasswordInput";
import { cn } from "@/lib/utils";

interface FormFieldProps<T extends FieldValues> {
  name: FieldPath<T>;
  control: Control<T>;
  label: string;
  type?: "text" | "email" | "password" | "number" | "tel" | "url";
  placeholder?: string;
  description?: string;
  required?: boolean;
  disabled?: boolean;
  autoComplete?: string;
  className?: string;
  children?: ReactNode;
}

export function FormField<T extends FieldValues>({
  name,
  control,
  label,
  type = "text",
  placeholder,
  description,
  required = false,
  disabled = false,
  autoComplete,
  className,
}: FormFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState: { error } }) => (
        <div className={cn("space-y-2", className)}>
          <Label htmlFor={name}>
            {label}
            {required && <span className="text-danger ml-1">*</span>}
          </Label>

          {type === "password" ? (
            <PasswordInput
              id={name}
              placeholder={placeholder}
              disabled={disabled}
              autoComplete={autoComplete}
              error={error?.message}
              {...field}
            />
          ) : (
            <Input
              id={name}
              type={type}
              placeholder={placeholder}
              disabled={disabled}
              autoComplete={autoComplete}
              error={error?.message}
              {...field}
            />
          )}

          {description && !error && (
            <p className="text-xs text-text-muted">{description}</p>
          )}

          {error && (
            <p className="text-xs text-danger" role="alert">
              {error.message}
            </p>
          )}
        </div>
      )}
    />
  );
}
