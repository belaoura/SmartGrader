import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HelpTooltip } from "@/components/ui/help-tooltip";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const INDIGO = "#6366F1";
const EMERALD = "#10B981";
const ROSE = "#F43F5E";

const CustomBarTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass rounded-lg px-3 py-2 text-sm shadow-lg border border-border">
        <p className="font-semibold font-heading">{label}</p>
        <p style={{ color: INDIGO }}>
          Avg Score: <strong>{payload[0].value.toFixed(1)}%</strong>
        </p>
      </div>
    );
  }
  return null;
};

const CustomPieTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass rounded-lg px-3 py-2 text-sm shadow-lg border border-border">
        <p className="font-semibold font-heading">{payload[0].name}</p>
        <p style={{ color: payload[0].payload.fill }}>
          {payload[0].value} students ({(payload[0].payload.percent * 100).toFixed(0)}%)
        </p>
      </div>
    );
  }
  return null;
};

export function ResultsBarChart({ data }) {
  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <CardTitle className="font-heading text-base text-foreground">Results by Exam</CardTitle>
          <HelpTooltip text="Average score percentage for each exam based on graded results." />
        </div>
        <p className="text-xs text-muted-foreground">Average score % per exam</p>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground text-sm">
            No exam data yet
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={INDIGO} stopOpacity={1} />
                  <stop offset="100%" stopColor={INDIGO} stopOpacity={0.5} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, className: "fill-muted-foreground" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, className: "fill-muted-foreground" }}
                axisLine={false}
                tickLine={false}
                domain={[0, 100]}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip content={<CustomBarTooltip />} cursor={{ fill: "rgba(99,102,241,0.08)" }} />
              <Bar
                dataKey="average"
                fill="url(#barGradient)"
                radius={[6, 6, 0, 0]}
                maxBarSize={60}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

const PIE_COLORS = [EMERALD, ROSE];

export function PassFailPieChart({ data }) {
  // Attach fill to each entry for custom tooltip
  const enriched = data.map((d, i) => ({ ...d, fill: PIE_COLORS[i % PIE_COLORS.length] }));
  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <CardTitle className="font-heading text-base text-foreground">Pass / Fail Distribution</CardTitle>
          <HelpTooltip text="Overall pass and fail distribution across all graded exams. Pass threshold is 50%." />
        </div>
        <p className="text-xs text-muted-foreground">
          {total > 0 ? `Based on ${total} graded results` : "No results yet — sample data shown"}
        </p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={enriched}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={105}
              paddingAngle={4}
              dataKey="value"
              strokeWidth={2}
              className="stroke-background"
            >
              {enriched.map((entry, index) => (
                <Cell key={index} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip content={<CustomPieTooltip />} />
            <Legend
              iconType="circle"
              iconSize={10}
              formatter={(value) => (
                <span className="text-xs text-foreground">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
