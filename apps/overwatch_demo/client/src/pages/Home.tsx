import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Zap, Shield, Activity, AlertCircle } from "lucide-react";
import { useValidation } from "@/hooks/useValidation";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import { ValidationBadge } from "@/components/ValidationBadge";
import { JsonOutput } from "@/components/JsonOutput";

export default function Home() {
  const [apiBase, setApiBase] = useState("http://localhost:8080");
  const [text, setText] = useState("");
  const healthCheck = useHealthCheck(apiBase);
  const validation = useValidation(apiBase);

  const loadExample = (example: string) => {
    if (example === "risky") {
      setText("This is 100% proven and guaranteed compliant. Trust me—nothing can go wrong. Act now before it's too late.");
    } else {
      setText("Based on limited information, this could be true, but you'd want to verify with primary sources. Here are assumptions and possible failure modes to test.");
    }
  };

  const handleValidate = async () => {
    await validation.validate(text);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      {/* Hero Section */}
      <div
        className="relative overflow-hidden bg-slate-900 text-white py-20 px-4"
        style={{
          backgroundImage:
            "url('https://private-us-east-1.manuscdn.com/sessionFile/pjiikJnj1MUElGTgB8gj3D/sandbox/WgknUO1DQzvq1tgLBgyOz8-img-1_1771182504000_na1fn_bHVtaW5hcmstaGVyby1iZw.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvcGppaWtKbmoxTVVFbEdUZ0I4Z2ozRC9zYW5kYm94L1dna25VTzFEUXp2cTF0Z0xCZ3lPejgtaW1nLTFfMTc3MTE4MjUwNDAwMF9uYTFmbl9iSFZ0YVc1aGNtc3RhR1Z5YnkxaVp3LnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSx3XzE5MjAsaF8xOTIwL2Zvcm1hdCx3ZWJwL3F1YWxpdHkscV84MCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=F8CcOmMQcc2mrZO~YKkJ9k3pjEmVM7BuXVas~gOCkZ~5idH~2KiKojjD9PrPq~WapMx9h7Sn9L9OrBNbPK0JmtQ7BBzLsim0tfev000FohE6rnXueLB8tPslYZRK7-uTKJbgG4DLezzfSBJGFywDDErLEsiUnIzndmL-~JA9NjKbDzJa9HxG7k4ggyVUy2Z17OBfh3LzuwV8bvS2pT1X2mbHdqCmjN38fosHG96UO4LLS8sai2n1-32bnnNQBtdfKpVY7lxCQFGACK~RiXPXlteun9yY62YBDQPs-4I9mRIZG8srTQ9eHMbi--7S1QkSdrlv8aZDEHKid6GRvl85ow__')",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="absolute inset-0 bg-black/60"></div>
        <div className="relative max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-8 h-8 text-cyan-400" />
            <span className="text-cyan-400 font-mono text-sm font-semibold tracking-widest">LUMINARK</span>
          </div>
          <h1 className="text-5xl font-mono font-bold mb-4 tracking-tight">Overwatch Demo</h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Real-time AI output validation and audit-ready compliance checking. Ensure every AI-generated response meets your standards.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* API Configuration */}
        <Card className="mb-8 border-slate-200 shadow-sm">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-500" />
              <CardTitle className="text-lg font-mono">API Configuration</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <label className="text-sm font-medium text-slate-700 block mb-2">API Base URL</label>
                <Input
                  type="text"
                  value={apiBase}
                  onChange={(e) => setApiBase(e.target.value)}
                  className="font-mono text-sm"
                  placeholder="http://localhost:8080"
                />
              </div>
              <Button
                onClick={() => healthCheck.check()}
                disabled={healthCheck.loading}
                variant="outline"
                className="border-slate-300 hover:bg-slate-50"
              >
                {healthCheck.loading ? "Checking..." : "Health Check"}
              </Button>
              <span
                className={`text-sm font-mono min-w-max ${
                  healthCheck.ok ? "text-green-600" : "text-red-600"
                }`}
              >
                {healthCheck.message}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Input Section */}
        <Card className="mb-8 border-slate-200 shadow-sm">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-cyan-500" />
              <CardTitle className="text-lg font-mono">Validation Input</CardTitle>
            </div>
            <CardDescription>Paste AI output or text to validate for compliance and quality</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button
                onClick={() => loadExample("risky")}
                variant="outline"
                size="sm"
                className="border-slate-300 hover:bg-slate-50"
              >
                Load Risky Example
              </Button>
              <Button
                onClick={() => loadExample("safe")}
                variant="outline"
                size="sm"
                className="border-slate-300 hover:bg-slate-50"
              >
                Load Safe Example
              </Button>
            </div>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste an AI output here..."
              className="font-mono text-sm min-h-[180px] border-slate-300"
            />
            <div className="flex gap-2 items-center">
              <Button
                onClick={handleValidate}
                disabled={validation.loading || !text.trim()}
                className="bg-cyan-500 hover:bg-cyan-600 text-white font-mono"
              >
                {validation.loading ? "Validating..." : "Validate"}
              </Button>
              {validation.error && (
                <span className="text-sm font-mono text-red-600">{validation.error}</span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Validation Result */}
          <div className="lg:col-span-1">
            <Card className="border-slate-200 shadow-sm h-full">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-mono">Validation Result</CardTitle>
              </CardHeader>
              <CardContent>
                {validation.result ? (
                  <div className="space-y-4">
                    <ValidationBadge
                      badge={validation.result.badge}
                      score={validation.result.overall_score || 0}
                    />
                    <div className="text-xs text-slate-500 p-3 bg-slate-50 rounded border border-slate-200">
                      Validation complete. Review the audit-ready response for detailed analysis.
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm font-mono">No validation yet</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Raw Response */}
          <div className="lg:col-span-2">
            <Card className="border-slate-200 shadow-sm h-full">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-mono">Audit-Ready Response</CardTitle>
                <CardDescription className="text-xs">Raw JSON output for compliance records</CardDescription>
              </CardHeader>
              <CardContent>
                <JsonOutput data={validation.result} />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-12 pt-8 border-t border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-mono font-bold text-sm text-slate-900 mb-2">Brand</h3>
              <p className="text-sm text-slate-600">
                <span className="font-semibold">LUMINARK</span> · Legal: Meridian Axiom Alignment Technologies (Ma'at)
              </p>
            </div>
            <div>
              <h3 className="font-mono font-bold text-sm text-slate-900 mb-2">Demo Flow</h3>
              <p className="text-sm text-slate-600">
                1. Load risky example → 2. Validate → 3. Load safe example → 4. Validate
              </p>
            </div>
            <div>
              <h3 className="font-mono font-bold text-sm text-slate-900 mb-2">Status</h3>
              <p className="text-sm text-slate-600">
                Audit-ready validation engine for AI output compliance
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
