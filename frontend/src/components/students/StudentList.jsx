import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function StudentList({ students }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Matricule</TableHead>
          <TableHead>Email</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {students.map((s) => (
          <TableRow key={s.id} className="hover:bg-accent/50 transition-colors">
            <TableCell className="font-medium">{s.name}</TableCell>
            <TableCell>{s.matricule}</TableCell>
            <TableCell>{s.email || "-"}</TableCell>
          </TableRow>
        ))}
        {students.length === 0 && (
          <TableRow>
            <TableCell colSpan={3} className="text-center text-muted-foreground py-8">
              No students yet.
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
