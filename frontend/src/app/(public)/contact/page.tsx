"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { contactSchema, type ContactFormData } from "@/lib/validations";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/forms";
import { Textarea } from "@/components/forms/Textarea";
import { Label } from "@/components/ui/Label";
import { Controller } from "react-hook-form";
import { api, isSuccess } from "@/lib/api";
import { toast } from "@/components/feedback/Toaster";
import { Mail, Send, Loader2, CheckCircle, MessageSquare } from "lucide-react";

export default function ContactPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const form = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: "",
      email: "",
      queryType: "general",
      message: "",
    },
  });

  const handleSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true);

    const response = await api.post("/contact", {
      name: data.name,
      email: data.email,
      query_type: data.queryType,
      message: data.message,
    });

    if (isSuccess(response)) {
      toast.success("Message sent successfully!");
      setIsSubmitted(true);
      form.reset();
    } else {
      toast.error(response.message || "Failed to send message");
    }

    setIsSubmitting(false);
  };

  if (isSubmitted) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 sm:px-6 lg:px-8">
        <Card variant="glass" className="text-center">
          <CardContent className="py-12">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-success/20">
              <CheckCircle className="h-8 w-8 text-success" />
            </div>
            <h2 className="font-display text-2xl font-bold text-text-high">
              Message Sent!
            </h2>
            <p className="mt-2 text-text-muted">
              Thank you for reaching out. We&apos;ll get back to you as soon as possible.
            </p>
            <Button
              onClick={() => setIsSubmitted(false)}
              variant="outline"
              className="mt-6"
            >
              Send Another Message
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-12 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/20">
          <MessageSquare className="h-8 w-8 text-primary" />
        </div>
        <h1 className="font-display text-4xl font-bold text-text-high">
          Contact Us
        </h1>
        <p className="mt-4 text-lg text-text-muted">
          Have a question, suggestion, or found a bug? We&apos;d love to hear from you!
        </p>
      </div>

      {/* Contact Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-primary" />
            Send us a message
          </CardTitle>
          <CardDescription>
            Fill out the form below and we&apos;ll respond as soon as possible.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                name="name"
                control={form.control}
                label="Your Name"
                placeholder="John Doe"
                required
              />
              <FormField
                name="email"
                control={form.control}
                label="Email Address"
                type="email"
                placeholder="john@example.com"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="queryType">
                Query Type <span className="text-danger">*</span>
              </Label>
              <Controller
                name="queryType"
                control={form.control}
                render={({ field }) => (
                  <select
                    id="queryType"
                    {...field}
                    className="w-full rounded-lg border border-surface-700 bg-surface-800 px-3 py-2 text-text-high transition-colors hover:border-primary/50 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary-glow"
                  >
                    <option value="general">General Inquiry</option>
                    <option value="bug">Bug Report</option>
                    <option value="suggestion">Feature Suggestion</option>
                  </select>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">
                Message <span className="text-danger">*</span>
              </Label>
              <Controller
                name="message"
                control={form.control}
                render={({ field, fieldState: { error } }) => (
                  <>
                    <Textarea
                      id="message"
                      placeholder="Tell us what's on your mind..."
                      className="min-h-[150px]"
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

            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full sm:w-auto"
              size="lg"
            >
              {isSubmitting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Send className="mr-2 h-4 w-4" />
              )}
              Send Message
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Contact Info */}
      <div className="mt-12 text-center text-text-muted">
        <p>
          You can also reach us at{" "}
          <a
            href="mailto:support@omnitool.app"
            className="text-primary hover:underline"
          >
            support@omnitool.app
          </a>
        </p>
      </div>
    </div>
  );
}
