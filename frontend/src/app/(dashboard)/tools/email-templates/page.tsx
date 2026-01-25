"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import {
  TemplateForm,
  TemplateCard,
  Pagination,
} from "@/components/features/email-templates";
import { api, isSuccess } from "@/lib/api";
import { toast } from "@/store/uiStore";
import type { EmailTemplate } from "@/types";
import type { EmailTemplateFormData } from "@/lib/validations";
import { Mail, Plus, Search, Loader2, X } from "lucide-react";

const ITEMS_PER_PAGE = 8;

interface TemplatesResponse {
  templates: EmailTemplate[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export default function EmailTemplatesPage() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);

  const fetchTemplates = useCallback(async () => {
    setIsLoading(true);
    const response = await api.get<TemplatesResponse>("/tools/email-templates", {
      params: {
        page: currentPage,
        per_page: ITEMS_PER_PAGE,
        search: searchQuery,
      },
    });

    if (isSuccess(response)) {
      setTemplates(response.data.templates);
      setTotalPages(response.data.total_pages);
    } else {
      toast.error(response.message || "Failed to load templates");
    }
    setIsLoading(false);
  }, [currentPage, searchQuery]);

  useEffect(() => {
    const loadTemplates = async () => {
      await fetchTemplates();
    };
    loadTemplates();
  }, [fetchTemplates]);

  const handleCreate = async (data: EmailTemplateFormData) => {
    setIsSaving(true);
    const response = await api.post("/tools/email-templates", data);

    if (isSuccess(response)) {
      toast.success("Template created successfully");
      setShowForm(false);
      fetchTemplates();
    } else {
      const errorMessage = typeof response.message === 'string' 
        ? response.message 
        : (response.message as unknown as { message?: string })?.message || "Failed to create template";
      toast.error(errorMessage);
    }
    setIsSaving(false);
  };

  const handleUpdate = async (data: EmailTemplateFormData) => {
    if (!editingTemplate) return;

    setIsSaving(true);
    const response = await api.put(`/tools/email-templates/${editingTemplate.id}`, data);

    if (isSuccess(response)) {
      toast.success("Template updated successfully");
      setEditingTemplate(null);
      fetchTemplates();
    } else {
      const errorMessage = typeof response.message === 'string' 
        ? response.message 
        : (response.message as unknown as { message?: string })?.message || "Failed to update template";
      toast.error(errorMessage);
    }
    setIsSaving(false);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this template?")) return;

    const response = await api.delete(`/tools/email-templates/${id}`);

    if (isSuccess(response)) {
      toast.success("Template deleted successfully");
      fetchTemplates();
    } else {
      const errorMessage = typeof response.message === 'string' 
        ? response.message 
        : (response.message as unknown as { message?: string })?.message || "Failed to delete template";
      toast.error(errorMessage);
    }
  };

  const handleEdit = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setShowForm(false);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchTemplates();
  };

  const clearSearch = () => {
    setSearchQuery("");
    setCurrentPage(1);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-high">
            Email Templates
          </h1>
          <p className="mt-2 text-text-muted">
            Create, manage, and copy your email templates.
          </p>
        </div>
        {!showForm && !editingTemplate && (
          <Button onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Template
          </Button>
        )}
      </div>

      {/* Create/Edit Form */}
      {(showForm || editingTemplate) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5 text-primary" />
              {editingTemplate ? "Edit Template" : "Create New Template"}
            </CardTitle>
            <CardDescription>
              {editingTemplate
                ? "Update your email template details."
                : "Create a new reusable email template."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TemplateForm
              initialData={
                editingTemplate
                  ? { title: editingTemplate.title, content: editingTemplate.content }
                  : undefined
              }
              onSubmit={editingTemplate ? handleUpdate : handleCreate}
              onCancel={() => {
                setShowForm(false);
                setEditingTemplate(null);
              }}
              isLoading={isSaving}
              submitLabel={editingTemplate ? "Update Template" : "Create Template"}
            />
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search templates..."
            className="pl-10"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-high"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <Button type="submit" variant="secondary">
          Search
        </Button>
      </form>

      {/* Templates Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : templates.length === 0 ? (
        <Card variant="glass">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Mail className="h-12 w-12 text-text-muted mb-4" />
            <p className="text-text-muted text-center">
              {searchQuery
                ? "No templates found matching your search."
                : "No templates yet. Create your first one!"}
            </p>
            {!searchQuery && !showForm && (
              <Button onClick={() => setShowForm(true)} className="mt-4">
                <Plus className="mr-2 h-4 w-4" />
                Create Template
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {templates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {/* Pagination */}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </>
      )}
    </div>
  );
}
