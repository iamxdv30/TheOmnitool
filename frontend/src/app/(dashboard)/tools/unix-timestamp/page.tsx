"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
} from "@/components/ui";
import { Clock, Calendar, ArrowRightLeft, Copy, Check } from "lucide-react";
import { toast } from "@/store/uiStore";

export default function UnixTimestampPage() {
  const [currentTimestamp, setCurrentTimestamp] = useState(Math.floor(Date.now() / 1000));
  const [inputTimestamp, setInputTimestamp] = useState("");
  const [timestampResult, setTimestampResult] = useState<{
    date: string;
    utc: string;
    relative: string;
  } | null>(null);

  const [inputDate, setInputDate] = useState("");
  const [dateResult, setDateResult] = useState<number | null>(null);
  
  const [copied, setCopied] = useState<string | null>(null);

  // Update current timestamp every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTimestamp(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleTimestampConvert = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputTimestamp) return;

    try {
      const ts = parseInt(inputTimestamp);
      if (isNaN(ts)) throw new Error("Invalid timestamp");

      // Handle milliseconds if it looks like one (13 digits)
      const date = new Date(inputTimestamp.length >= 13 ? ts : ts * 1000);
      
      if (isNaN(date.getTime())) throw new Error("Invalid date");

      setTimestampResult({
        date: date.toLocaleString(),
        utc: date.toUTCString(),
        relative: getRelativeTime(date),
      });
    } catch (err) {
      toast.error("Please enter a valid Unix timestamp.");
    }
  };

  const handleDateConvert = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputDate) return;

    try {
      const date = new Date(inputDate);
      if (isNaN(date.getTime())) throw new Error("Invalid date");

      setDateResult(Math.floor(date.getTime() / 1000));
    } catch (err) {
      toast.error("Please enter a valid date and time.");
    }
  };

  const getRelativeTime = (date: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((date.getTime() - now.getTime()) / 1000);
    
    const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
    
    if (Math.abs(diffInSeconds) < 60) return rtf.format(diffInSeconds, "second");
    if (Math.abs(diffInSeconds) < 3600) return rtf.format(Math.floor(diffInSeconds / 60), "minute");
    if (Math.abs(diffInSeconds) < 86400) return rtf.format(Math.floor(diffInSeconds / 3600), "hour");
    return rtf.format(Math.floor(diffInSeconds / 86400), "day");
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
    toast.success(`${label} copied to clipboard!`);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="font-display text-3xl font-bold text-text-high">
          Unix Timestamp Converter
        </h1>
        <p className="mt-2 text-text-muted">
          Convert between Unix timestamps and human-readable dates.
        </p>
      </div>

      {/* Current Timestamp Card */}
      <Card variant="glass" className="border-primary/20">
        <CardContent className="flex flex-col items-center justify-between gap-4 p-6 sm:flex-row">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-primary">
              <Clock className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-muted uppercase tracking-wider">
                Current Unix Timestamp
              </p>
              <p className="font-mono text-3xl font-bold text-text-high">
                {currentTimestamp}
              </p>
            </div>
          </div>
          <Button 
            variant="outline" 
            onClick={() => copyToClipboard(currentTimestamp.toString(), "Current Timestamp")}
            className="w-full sm:w-auto"
          >
            {copied === "Current Timestamp" ? <Check className="mr-2 h-4 w-4" /> : <Copy className="mr-2 h-4 w-4" />}
            Copy Timestamp
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-8 md:grid-cols-2">
        {/* Timestamp to Date */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-warning" />
              Timestamp to Date
            </CardTitle>
            <CardDescription>
              Convert a Unix timestamp to local and UTC time.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleTimestampConvert} className="space-y-4">
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="e.g. 1737867805"
                  className="w-full rounded-lg border border-surface-600 bg-surface-800 px-4 py-2 text-text-high focus:border-primary focus:outline-none"
                  value={inputTimestamp}
                  onChange={(e) => setInputTimestamp(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full" variant="glow">
                <ArrowRightLeft className="mr-2 h-4 w-4" />
                Convert
              </Button>
            </form>

            {timestampResult && (
              <div className="mt-6 space-y-3 rounded-lg bg-surface-800 p-4 border border-surface-700">
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase">Local Time</p>
                  <p className="text-sm font-medium text-text-high">{timestampResult.date}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase">UTC Time</p>
                  <p className="text-sm font-medium text-text-high">{timestampResult.utc}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase">Relative</p>
                  <p className="text-sm font-medium text-text-high">{timestampResult.relative}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Date to Timestamp */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-secondary" />
              Date to Timestamp
            </CardTitle>
            <CardDescription>
              Convert a human date to a Unix timestamp.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleDateConvert} className="space-y-4">
              <div className="space-y-2">
                <input
                  type="datetime-local"
                  className="w-full rounded-lg border border-surface-600 bg-surface-800 px-4 py-2 text-text-high focus:border-primary focus:outline-none"
                  value={inputDate}
                  onChange={(e) => setInputDate(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full" variant="glow">
                <ArrowRightLeft className="mr-2 h-4 w-4" />
                Convert
              </Button>
            </form>

            {dateResult !== null && (
              <div className="mt-6 space-y-3 rounded-lg bg-surface-800 p-4 border border-surface-700 text-center">
                <p className="text-xs font-medium text-text-muted uppercase tracking-wider">Unix Timestamp</p>
                <p className="font-mono text-2xl font-bold text-text-high">{dateResult}</p>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => copyToClipboard(dateResult.toString(), "Converted Timestamp")}
                  className="mt-2"
                >
                  {copied === "Converted Timestamp" ? <Check className="mr-2 h-4 w-4" /> : <Copy className="mr-2 h-4 w-4" />}
                  Copy Result
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info Section */}
      <Card variant="glass">
        <CardContent className="p-6">
          <h3 className="mb-2 font-display text-lg font-semibold text-text-high">What is a Unix Timestamp?</h3>
          <p className="text-text-muted">
            The Unix epoch (or Unix time or POSIX time or Unix timestamp) is the number of seconds that have elapsed since January 1, 1970 (midnight UTC/GMT), not counting leap seconds (in ISO 8601: 1970-01-01T00:00:00Z).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
