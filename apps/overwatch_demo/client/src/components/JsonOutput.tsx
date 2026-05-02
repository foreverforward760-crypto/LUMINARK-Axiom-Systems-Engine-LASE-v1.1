import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface JsonOutputProps {
  data: Record<string, unknown> | null;
  className?: string;
}

export function JsonOutput({ data, className }: JsonOutputProps) {
  const [copied, setCopied] = useState(false);

  const jsonString = data ? JSON.stringify(data, null, 2) : "{}";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className={cn("relative", className)}>
      <Button
        onClick={handleCopy}
        size="sm"
        variant="ghost"
        className="absolute top-2 right-2 h-8 w-8 p-0 hover:bg-slate-200"
        title="Copy to clipboard"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-600" />
        ) : (
          <Copy className="w-4 h-4 text-slate-500" />
        )}
      </Button>
      <pre className="bg-slate-50 border border-slate-300 rounded p-4 text-xs font-mono overflow-auto max-h-96 text-slate-800 pr-12">
        {jsonString}
      </pre>
    </div>
  );
}
