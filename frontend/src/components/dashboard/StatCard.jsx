import { Card, CardContent } from "@/components/ui/card";

export default function StatCard({ icon: Icon, label, value }) {
  return (
    <Card className="transition-shadow hover:shadow-md cursor-default">
      <CardContent className="flex items-center gap-4 p-6">
        <div className="rounded-lg bg-primary/10 p-3">
          <Icon className="h-6 w-6 text-primary" />
        </div>
        <div>
          <p className="text-2xl font-bold font-heading">{value}</p>
          <p className="text-sm text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}
