"use client";

import { useState, useEffect } from "react";
import { useAuth, useProfile } from "@/hooks";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui";
import {
  Calculator,
  FileText,
  Mail,
  ArrowRight,
  Loader2,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";

interface UserTool {
  id: number;
  name: string;
  display_name: string;
  description: string;
  route: string;
}

const toolIconMap: Record<string, LucideIcon> = {
  "tax-calculator": Calculator,
  "unified-tax-calculator": Calculator,
  "char-counter": FileText,
  "character-counter": FileText,
  "email-templates": Mail,
};

const toolColorMap: Record<string, string> = {
  "tax-calculator": "text-primary",
  "unified-tax-calculator": "text-primary",
  "char-counter": "text-secondary",
  "character-counter": "text-secondary",
  "email-templates": "text-accent",
};

export default function DashboardPage() {
  const { user } = useAuth();
  const { getUserTools } = useProfile();
  const [tools, setTools] = useState<UserTool[]>([]);
  const [isToolsLoading, setIsToolsLoading] = useState(true);

  useEffect(() => {
    async function loadTools() {
      setIsToolsLoading(true);
      const userTools = await getUserTools();
      setTools(userTools);
      setIsToolsLoading(false);
    }
    loadTools();
  }, [getUserTools]);

  const getToolIcon = (toolName: string): LucideIcon => {
    return toolIconMap[toolName] || Wrench;
  };

  const getToolColor = (toolName: string): string => {
    return toolColorMap[toolName] || "text-primary";
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="font-display text-3xl font-bold text-text-high">
          Welcome back, {user?.username || "User"}
        </h1>
        <p className="mt-2 text-text-muted">
          Access your tools and manage your account from here.
        </p>
      </div>

      {/* Tools Grid */}
      <div>
        <h2 className="mb-4 font-display text-xl font-semibold text-text-high">
          Your Tools
        </h2>
        {isToolsLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : tools.length === 0 ? (
          <Card variant="glass">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Wrench className="h-12 w-12 text-text-muted mb-4" />
              <p className="text-text-muted text-center">
                No tools available. Contact an administrator to get access.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tools.map((tool) => {
              const Icon = getToolIcon(tool.name);
              const color = getToolColor(tool.name);
              return (
                <Link key={tool.id} href={tool.route}>
                  <Card
                    variant="interactive"
                    className="h-full transition-all hover:border-primary/50"
                  >
                    <CardHeader>
                      <div
                        className={`mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-surface-700 ${color}`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                      <CardTitle className="text-lg">{tool.display_name}</CardTitle>
                      <CardDescription>{tool.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center text-sm text-primary">
                        Open tool
                        <ArrowRight className="ml-1 h-4 w-4" />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div>
        <h2 className="mb-4 font-display text-xl font-semibold text-text-high">
          Account Info
        </h2>
        <Card variant="glass">
          <CardContent className="grid gap-4 p-6 sm:grid-cols-3">
            <div>
              <p className="text-sm text-text-muted">Email</p>
              <p className="font-medium text-text-high">{user?.email}</p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Role</p>
              <p className="font-medium capitalize text-text-high">
                {user?.role}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Status</p>
              <p className="font-medium text-success">
                {user?.email_verified ? "Verified" : "Pending Verification"}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
