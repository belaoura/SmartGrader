import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { useTheme } from "@/hooks/use-theme";

export default function Settings() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold font-heading">Settings</h2>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-base">Appearance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Dark Mode</Label>
              <p className="text-sm text-muted-foreground">Toggle dark theme</p>
            </div>
            <Switch
              checked={theme === "dark"}
              onCheckedChange={toggleTheme}
              className="cursor-pointer"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-base">About</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><span className="font-medium">Application:</span> SmartGrader</p>
          <p><span className="font-medium">Version:</span> 0.2.0</p>
          <Separator />
          <p className="text-muted-foreground">
            Academic Exam Management System with AI-Powered Grading.
            Final Year Project (PFE).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
