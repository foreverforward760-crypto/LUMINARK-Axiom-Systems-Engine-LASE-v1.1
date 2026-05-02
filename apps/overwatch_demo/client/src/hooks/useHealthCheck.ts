import { useState, useCallback } from "react";

export interface HealthStatus {
  ok: boolean;
  message: string;
  loading: boolean;
}

export function useHealthCheck(apiBase: string) {
  const [status, setStatus] = useState<HealthStatus>({
    ok: false,
    message: "Not checked",
    loading: false,
  });

  const check = useCallback(async () => {
    setStatus({ ok: false, message: "Checking...", loading: true });

    try {
      const response = await fetch(`${apiBase}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setStatus({
        ok: data.ok === true,
        message: data.ok ? "API is healthy ✅" : "API returned unhealthy status",
        loading: false,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? `Connection failed: ${err.message}` : "Connection failed";
      setStatus({
        ok: false,
        message: errorMessage,
        loading: false,
      });
    }
  }, [apiBase]);

  return { ...status, check };
}
