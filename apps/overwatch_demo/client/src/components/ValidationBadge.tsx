import { CheckCircle2, AlertCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ValidationBadgeProps {
  badge: "pass" | "caution" | "fail";
  score: number;
  className?: string;
}

export function ValidationBadge({ badge, score, className }: ValidationBadgeProps) {
  const badgeConfig = {
    pass: {
      icon: CheckCircle2,
      bg: "bg-green-50",
      text: "text-green-700",
      border: "border-green-200",
      label: "PASS",
    },
    caution: {
      icon: AlertCircle,
      bg: "bg-amber-50",
      text: "text-amber-700",
      border: "border-amber-200",
      label: "CAUTION",
    },
    fail: {
      icon: XCircle,
      bg: "bg-red-50",
      text: "text-red-700",
      border: "border-red-200",
      label: "FAIL",
    },
  };

  const config = badgeConfig[badge];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        `p-4 rounded-lg border-2 ${config.bg} ${config.text}`,
        className
      )}
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-5 h-5" />
        <span className="font-mono font-bold text-sm uppercase">{config.label}</span>
      </div>
      <div className="text-3xl font-mono font-bold">{score.toFixed(2)}</div>
      <div className="text-xs opacity-75 mt-1">Compliance Score</div>
    </div>
  );
}
