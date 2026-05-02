import { useState, useCallback } from "react";

export interface ValidationResult {
  badge: "pass" | "caution" | "fail";
  overall_score: number;
  [key: string]: unknown;
}

export interface ValidationState {
  result: ValidationResult | null;
  loading: boolean;
  error: string | null;
}

export function useValidation(apiBase: string) {
  const [state, setState] = useState<ValidationState>({
    result: null,
    loading: false,
    error: null,
  });

  const validate = useCallback(
    async (text: string) => {
      if (!text.trim()) {
        setState({ result: null, loading: false, error: "Text cannot be empty" });
        return;
      }

      setState({ result: null, loading: true, error: null });

      try {
        const response = await fetch(`${apiBase}/validate`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            text,
            source: "overwatch-demo",
            meta: { demo: true, timestamp: new Date().toISOString() },
          }),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        setState({ result: data, loading: false, error: null });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Validation failed";
        setState({ result: null, loading: false, error: errorMessage });
      }
    },
    [apiBase]
  );

  const reset = useCallback(() => {
    setState({ result: null, loading: false, error: null });
  }, []);

  return { ...state, validate, reset };
}
