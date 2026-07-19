"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { Copy, Edit, Trash2, Check, MoreVertical } from "lucide-react";
import type { EmailTemplate } from "@/types";

interface TemplateCardProps {
  template: EmailTemplate;
  onEdit: (template: EmailTemplate) => void;
  onDelete: (id: number) => void;
}

export function TemplateCard({ template, onEdit, onDelete }: TemplateCardProps) {
  const [copied, setCopied] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(template.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <Card className="group relative transition-all hover:border-primary/50">
      <CardContent className="p-4">
        {/* Header */}
        <div className="mb-3 flex items-start justify-between">
          <h3 className="font-medium text-text-high line-clamp-1 pr-8">
            {template.title}
          </h3>
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowMenu(!showMenu)}
              className="h-8 w-8 p-0"
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
            {showMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 top-8 z-20 w-32 rounded-lg border border-surface-700 bg-surface-800 py-1 shadow-lg">
                  <button
                    onClick={() => {
                      onEdit(template);
                      setShowMenu(false);
                    }}
                    className="flex w-full items-center gap-2 px-3 py-2 text-sm text-text-high hover:bg-surface-700"
                  >
                    <Edit className="h-4 w-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      onDelete(template.id);
                      setShowMenu(false);
                    }}
                    className="flex w-full items-center gap-2 px-3 py-2 text-sm text-danger hover:bg-surface-700"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Content Preview */}
        <p className="mb-4 text-sm text-text-muted line-clamp-3">
          {template.content}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted">
            {formatDate(template.updated_at || template.created_at)}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="h-8"
          >
            {copied ? (
              <>
                <Check className="mr-1 h-4 w-4 text-success" />
                Copied
              </>
            ) : (
              <>
                <Copy className="mr-1 h-4 w-4" />
                Copy
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
