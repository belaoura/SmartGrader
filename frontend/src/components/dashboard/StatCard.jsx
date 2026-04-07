import { TrendingUp } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const colorMap = {
  indigo: {
    border: "border-l-indigo-500",
    iconBg: "bg-indigo-500/10",
    iconColor: "text-indigo-500",
  },
  violet: {
    border: "border-l-violet-500",
    iconBg: "bg-violet-500/10",
    iconColor: "text-violet-500",
  },
  emerald: {
    border: "border-l-emerald-500",
    iconBg: "bg-emerald-500/10",
    iconColor: "text-emerald-500",
  },
  amber: {
    border: "border-l-amber-500",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-500",
  },
};

export default function StatCard({ icon: Icon, label, value, color = "indigo", trend }) {
  const c = colorMap[color] || colorMap.indigo;

  return (
    <Card
      className={`border-l-4 ${c.border} hover:-translate-y-1 hover:shadow-lg transition-all duration-200 cursor-pointer`}
    >
      <CardContent className="flex items-center gap-4 p-6">
        <div className={`rounded-xl ${c.iconBg} p-3 shrink-0`}>
          <Icon className={`h-6 w-6 ${c.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-3xl font-extrabold font-heading tracking-tight leading-none">
            {value}
          </p>
          <p className="text-sm text-muted-foreground mt-0.5">{label}</p>
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1 text-emerald-500 text-xs font-medium shrink-0">
            <TrendingUp className="h-3 w-3" />
            <span>{trend}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
