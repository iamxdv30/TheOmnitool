"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui";
import { X, Loader2, Check, Plus } from "lucide-react";
import type { AdminUser, Tool } from "@/types";
import { api, isSuccess } from "@/lib/api";

interface ToolAccessDialogProps {
  isOpen: boolean;
  user: AdminUser | null;
  onClose: () => void;
  onGrant: (userId: number, toolName: string) => Promise<void>;
  onRevoke: (userId: number, toolName: string) => Promise<void>;
  isLoading?: boolean;
}

export function ToolAccessDialog({
  isOpen,
  user,
  onClose,
  onGrant,
  onRevoke,
  isLoading = false,
}: ToolAccessDialogProps) {
  const [allTools, setAllTools] = useState<Tool[]>([]);
  const [loadingTools, setLoadingTools] = useState(true);
  const [processingTool, setProcessingTool] = useState<string | null>(null);

  useEffect(() => {
    const fetchTools = async () => {
      setLoadingTools(true);
      const response = await api.get<{ tools: Tool[] }>("/admin/tools");
      if (isSuccess(response)) {
        setAllTools(response.data.tools);
      }
      setLoadingTools(false);
    };

    if (isOpen) {
      fetchTools();
    }
  }, [isOpen]);

  const handleToggle = async (toolName: string, hasAccess: boolean) => {
    if (!user) return;
    setProcessingTool(toolName);
    
    if (hasAccess) {
      await onRevoke(user.id, toolName);
    } else {
      await onGrant(user.id, toolName);
    }
    
    setProcessingTool(null);
  };

  if (!isOpen || !user) return null;

  const userTools = user.tools || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <Card className="relative z-10 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>
            Tool Access: {user.username}
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          {loadingTools ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : allTools.length === 0 ? (
            <p className="py-8 text-center text-text-muted">No tools available</p>
          ) : (
            <div className="space-y-2">
              {allTools.map((tool) => {
                const hasAccess = userTools.includes(tool.name);
                const isProcessing = processingTool === tool.name;

                return (
                  <div
                    key={tool.id}
                    className="flex items-center justify-between rounded-lg border border-surface-700 p-3"
                  >
                    <div>
                      <p className="font-medium text-text-high">{tool.display_name}</p>
                      <p className="text-sm text-text-muted">{tool.description}</p>
                    </div>
                    <Button
                      variant={hasAccess ? "secondary" : "primary"}
                      size="sm"
                      onClick={() => handleToggle(tool.name, hasAccess)}
                      disabled={isLoading || isProcessing}
                    >
                      {isProcessing ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : hasAccess ? (
                        <>
                          <Check className="mr-1 h-4 w-4" />
                          Granted
                        </>
                      ) : (
                        <>
                          <Plus className="mr-1 h-4 w-4" />
                          Grant
                        </>
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          )}

          <div className="mt-6 flex justify-end">
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
