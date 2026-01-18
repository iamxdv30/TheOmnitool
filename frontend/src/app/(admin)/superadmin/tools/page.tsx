"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/forms";
import { api, isSuccess } from "@/lib/api";
import { toast } from "@/components/feedback/Toaster";
import { useAuth } from "@/hooks";
import type { Tool } from "@/types";
import {
  Wrench,
  Plus,
  Edit,
  Trash2,
  Loader2,
  X,
  Save,
  ToggleLeft,
  ToggleRight,
} from "lucide-react";

const toolSchema = z.object({
  name: z.string().min(1, "Name is required").regex(/^[a-z0-9-]+$/, "Name must be lowercase with hyphens only"),
  display_name: z.string().min(1, "Display name is required"),
  description: z.string().min(1, "Description is required"),
  route: z.string().min(1, "Route is required").startsWith("/", "Route must start with /"),
  is_default: z.boolean(),
});

type ToolFormData = z.infer<typeof toolSchema>;

export default function ManageToolsPage() {
  const { user } = useAuth();
  const router = useRouter();

  const [tools, setTools] = useState<Tool[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingTool, setEditingTool] = useState<Tool | null>(null);

  const form = useForm<ToolFormData>({
    resolver: zodResolver(toolSchema),
    defaultValues: {
      name: "",
      display_name: "",
      description: "",
      route: "/tools/",
      is_default: false,
    },
  });

  useEffect(() => {
    if (user && user.role !== "superadmin") {
      router.push("/admin");
    }
  }, [user, router]);

  const fetchTools = useCallback(async () => {
    setIsLoading(true);
    const response = await api.get<{ tools: Tool[] }>("/admin/tools");

    if (isSuccess(response)) {
      setTools(response.data.tools);
    } else {
      toast.error(response.message || "Failed to load tools");
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    const loadTools = async () => {
      await fetchTools();
    };
    loadTools();
  }, [fetchTools]);

  const handleEdit = (tool: Tool) => {
    setEditingTool(tool);
    form.reset({
      name: tool.name,
      display_name: tool.display_name,
      description: tool.description,
      route: tool.route,
      is_default: tool.is_default,
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTool(null);
    form.reset({
      name: "",
      display_name: "",
      description: "",
      route: "/tools/",
      is_default: false,
    });
  };

  const handleSubmit = async (data: ToolFormData) => {
    setIsProcessing(true);

    if (editingTool) {
      const response = await api.put(`/admin/tools/${editingTool.id}`, data);

      if (isSuccess(response)) {
        toast.success("Tool updated successfully");
        handleCancel();
        fetchTools();
      } else {
        toast.error(response.message || "Failed to update tool");
      }
    } else {
      const response = await api.post("/admin/tools", data);

      if (isSuccess(response)) {
        toast.success("Tool created successfully");
        handleCancel();
        fetchTools();
      } else {
        toast.error(response.message || "Failed to create tool");
      }
    }

    setIsProcessing(false);
  };

  const handleDelete = async (toolId: number) => {
    if (!confirm("Are you sure you want to delete this tool? This will revoke access for all users.")) {
      return;
    }

    const response = await api.delete(`/admin/tools/${toolId}`);

    if (isSuccess(response)) {
      toast.success("Tool deleted successfully");
      fetchTools();
    } else {
      toast.error(response.message || "Failed to delete tool");
    }
  };

  const handleToggleDefault = async (tool: Tool) => {
    const response = await api.put(`/admin/tools/${tool.id}`, {
      ...tool,
      is_default: !tool.is_default,
    });

    if (isSuccess(response)) {
      toast.success(`Tool ${tool.is_default ? "removed from" : "set as"} default`);
      fetchTools();
    } else {
      toast.error(response.message || "Failed to update tool");
    }
  };

  if (user?.role !== "superadmin") {
    return null;
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-high flex items-center gap-3">
            <Wrench className="h-8 w-8 text-warning" />
            Manage Tools
          </h1>
          <p className="mt-2 text-text-muted">
            Create, edit, and configure system tools.
          </p>
        </div>
        {!showForm && (
          <Button onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Tool
          </Button>
        )}
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>
              {editingTool ? `Edit Tool: ${editingTool.display_name}` : "Create New Tool"}
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={handleCancel} className="h-8 w-8 p-0">
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  name="name"
                  control={form.control}
                  label="Tool Name (slug)"
                  placeholder="e.g., tax-calculator"
                  description="Lowercase with hyphens, used in URLs"
                  required
                  disabled={!!editingTool}
                />
                <FormField
                  name="display_name"
                  control={form.control}
                  label="Display Name"
                  placeholder="e.g., Tax Calculator"
                  required
                />
              </div>

              <FormField
                name="description"
                control={form.control}
                label="Description"
                placeholder="Brief description of what this tool does"
                required
              />

              <FormField
                name="route"
                control={form.control}
                label="Route"
                placeholder="/tools/tax-calculator"
                description="URL path for the tool"
                required
              />

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_default"
                  {...form.register("is_default")}
                  className="h-4 w-4 rounded border-surface-700 bg-surface-800 text-primary focus:ring-primary"
                />
                <label htmlFor="is_default" className="text-sm text-text-high cursor-pointer">
                  Default tool (automatically granted to new users)
                </label>
              </div>

              <div className="flex gap-2 pt-4">
                <Button type="submit" disabled={isProcessing}>
                  {isProcessing ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Save className="mr-2 h-4 w-4" />
                  )}
                  {editingTool ? "Update Tool" : "Create Tool"}
                </Button>
                <Button type="button" variant="ghost" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Tools Table */}
      <Card>
        <CardHeader>
          <CardTitle>System Tools</CardTitle>
          <CardDescription>
            Configure available tools and their default status.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : tools.length === 0 ? (
            <p className="py-8 text-center text-text-muted">No tools configured</p>
          ) : (
            <div className="overflow-hidden rounded-lg border border-surface-700">
              <table className="w-full">
                <thead className="bg-surface-800">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                      Tool
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                      Route
                    </th>
                    <th className="px-4 py-3 text-center text-sm font-medium text-text-muted">
                      Default
                    </th>
                    <th className="px-4 py-3 text-right text-sm font-medium text-text-muted">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-700">
                  {tools.map((tool) => (
                    <tr key={tool.id} className="hover:bg-surface-800/50">
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-text-high">{tool.display_name}</p>
                          <p className="text-sm text-text-muted">{tool.description}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-text-muted font-mono text-sm">
                        {tool.route}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleDefault(tool)}
                          className={tool.is_default ? "text-success" : "text-text-muted"}
                        >
                          {tool.is_default ? (
                            <ToggleRight className="h-5 w-5" />
                          ) : (
                            <ToggleLeft className="h-5 w-5" />
                          )}
                        </Button>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(tool)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(tool.id)}
                            className="text-danger hover:text-danger hover:bg-danger/10"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
