"use client";

import { useState, useMemo } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/forms/Textarea";
import { FileText, Hash, Type, AlignLeft, AlertTriangle, type LucideIcon } from "lucide-react";

const DEFAULT_CHAR_LIMIT = 3532;

interface TextStats {
  characters: number;
  charactersNoSpaces: number;
  words: number;
  sentences: number;
  paragraphs: number;
  lines: number;
}

function countStats(text: string): TextStats {
  const characters = text.length;
  const charactersNoSpaces = text.replace(/\s/g, "").length;
  const words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
  const sentences = text.trim() === "" ? 0 : (text.match(/[.!?]+/g) || []).length;
  const paragraphs = text.trim() === "" ? 0 : text.split(/\n\n+/).filter(p => p.trim()).length;
  const lines = text.trim() === "" ? 0 : text.split(/\n/).filter(l => l.trim()).length;

  return {
    characters,
    charactersNoSpaces,
    words,
    sentences,
    paragraphs,
    lines,
  };
}

export default function CharCounterPage() {
  const [text, setText] = useState("");
  const [charLimit, setCharLimit] = useState(DEFAULT_CHAR_LIMIT);

  const stats = useMemo(() => countStats(text), [text]);
  const isOverLimit = stats.characters > charLimit;
  const remainingChars = charLimit - stats.characters;
  const usagePercent = Math.min((stats.characters / charLimit) * 100, 100);

  const getProgressColor = () => {
    if (isOverLimit) return "bg-danger";
    if (usagePercent > 90) return "bg-warning";
    if (usagePercent > 70) return "bg-accent";
    return "bg-primary";
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-3xl font-bold text-text-high">
          Character Counter
        </h1>
        <p className="mt-2 text-text-muted">
          Count characters, words, sentences, and more in real-time.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Text Area */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Text Input
              </CardTitle>
              <CardDescription>
                Enter or paste your text below to analyze it.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Start typing or paste your text here..."
                className={`min-h-[300px] resize-y ${isOverLimit ? "border-danger focus:border-danger focus:ring-danger/20" : ""}`}
              />

              {/* Character Limit Input */}
              <div className="flex items-center gap-4">
                <Label htmlFor="charLimit" className="whitespace-nowrap">
                  Character Limit:
                </Label>
                <Input
                  id="charLimit"
                  type="number"
                  value={charLimit}
                  onChange={(e) => setCharLimit(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-32"
                  min={1}
                />
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-muted">Character Usage</span>
                  <span className={isOverLimit ? "text-danger font-medium" : "text-text-muted"}>
                    {stats.characters.toLocaleString()} / {charLimit.toLocaleString()}
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-surface-700">
                  <div
                    className={`h-full transition-all duration-300 ${getProgressColor()}`}
                    style={{ width: `${Math.min(usagePercent, 100)}%` }}
                  />
                </div>
                {isOverLimit && (
                  <div className="flex items-center gap-2 text-sm text-danger">
                    <AlertTriangle className="h-4 w-4" />
                    <span>{Math.abs(remainingChars).toLocaleString()} characters over limit</span>
                  </div>
                )}
                {!isOverLimit && remainingChars > 0 && (
                  <p className="text-sm text-text-muted">
                    {remainingChars.toLocaleString()} characters remaining
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stats Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hash className="h-5 w-5 text-primary" />
                Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <StatItem
                icon={Type}
                label="Characters"
                value={stats.characters.toLocaleString()}
                highlight={isOverLimit}
              />
              <StatItem
                icon={Type}
                label="Characters (no spaces)"
                value={stats.charactersNoSpaces.toLocaleString()}
              />
              <StatItem
                icon={AlignLeft}
                label="Words"
                value={stats.words.toLocaleString()}
              />
              <StatItem
                icon={FileText}
                label="Sentences"
                value={stats.sentences.toLocaleString()}
              />
              <StatItem
                icon={FileText}
                label="Paragraphs"
                value={stats.paragraphs.toLocaleString()}
              />
              <StatItem
                icon={FileText}
                label="Lines"
                value={stats.lines.toLocaleString()}
              />
            </CardContent>
          </Card>

          {/* Reading Time Estimate */}
          <Card variant="glass">
            <CardContent className="p-4">
              <p className="text-sm text-text-muted">Estimated Reading Time</p>
              <p className="font-display text-2xl font-bold text-text-high">
                {Math.ceil(stats.words / 200)} min
              </p>
              <p className="text-xs text-text-muted">Based on 200 words/min</p>
            </CardContent>
          </Card>

          {/* Speaking Time Estimate */}
          <Card variant="glass">
            <CardContent className="p-4">
              <p className="text-sm text-text-muted">Estimated Speaking Time</p>
              <p className="font-display text-2xl font-bold text-text-high">
                {Math.ceil(stats.words / 150)} min
              </p>
              <p className="text-xs text-text-muted">Based on 150 words/min</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

interface StatItemProps {
  icon: LucideIcon;
  label: string;
  value: string;
  highlight?: boolean;
}

function StatItem({ icon: Icon, label, value, highlight }: StatItemProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-text-muted">
        <Icon className="h-4 w-4" />
        <span className="text-sm">{label}</span>
      </div>
      <span className={`font-medium ${highlight ? "text-danger" : "text-text-high"}`}>
        {value}
      </span>
    </div>
  );
}
