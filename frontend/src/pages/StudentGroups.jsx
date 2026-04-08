import { useState } from "react";
import { Plus, ChevronDown, ChevronRight, Trash2, UserPlus, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { useGroups, useGroup, useCreateGroup, useDeleteGroup, useAddMembers, useRemoveMember } from "@/hooks/use-groups";
import { useStudents } from "@/hooks/use-students";

function GroupRow({ group, students }) {
  const [expanded, setExpanded] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);
  const { data: groupDetail, isLoading: loadingDetail } = useGroup(expanded ? group.id : null);
  const addMembers = useAddMembers();
  const removeMember = useRemoveMember();
  const deleteGroup = useDeleteGroup();

  const members = groupDetail?.members || [];
  const memberIds = new Set(members.map((m) => m.id));
  const availableStudents = (students || []).filter((s) => !memberIds.has(s.id));

  const toggleStudent = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleAddMembers = () => {
    if (selectedIds.length === 0) return;
    addMembers.mutate(
      { groupId: group.id, studentIds: selectedIds },
      { onSuccess: () => setSelectedIds([]) }
    );
  };

  const handleRemove = (studentId) => {
    removeMember.mutate({ groupId: group.id, studentId });
  };

  const handleDelete = () => {
    if (window.confirm(`Delete group "${group.name}"?`)) {
      deleteGroup.mutate(group.id);
    }
  };

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-accent/50 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-center gap-3">
          {expanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
          <span className="font-medium">{group.name}</span>
          <Badge variant="secondary">{group.member_count ?? 0} members</Badge>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-destructive hover:bg-destructive/10"
          onClick={(e) => { e.stopPropagation(); handleDelete(); }}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      {expanded && (
        <div className="border-t border-border bg-background/50 px-4 py-3 space-y-4">
          {loadingDetail ? (
            <div className="space-y-2">
              {[1, 2].map((i) => <Skeleton key={i} className="h-8 rounded" />)}
            </div>
          ) : (
            <>
              {/* Members list */}
              {members.length === 0 ? (
                <p className="text-sm text-muted-foreground">No members yet.</p>
              ) : (
                <div className="space-y-1">
                  {members.map((m) => (
                    <div key={m.id} className="flex items-center justify-between rounded px-3 py-1.5 hover:bg-accent/30">
                      <div>
                        <span className="text-sm font-medium">{m.name}</span>
                        <span className="ml-2 text-xs text-muted-foreground">{m.student_id}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive hover:bg-destructive/10"
                        onClick={() => handleRemove(m.id)}
                        disabled={removeMember.isPending}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}

              {/* Add members */}
              {availableStudents.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Add students</p>
                  <div className="max-h-40 overflow-y-auto space-y-1 border border-border rounded-lg p-2">
                    {availableStudents.map((s) => (
                      <label key={s.id} className="flex items-center gap-2 cursor-pointer rounded px-2 py-1 hover:bg-accent/30">
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(s.id)}
                          onChange={() => toggleStudent(s.id)}
                          className="rounded"
                        />
                        <span className="text-sm">{s.name}</span>
                        <span className="text-xs text-muted-foreground">{s.student_id}</span>
                      </label>
                    ))}
                  </div>
                  <Button
                    size="sm"
                    onClick={handleAddMembers}
                    disabled={selectedIds.length === 0 || addMembers.isPending}
                    className="cursor-pointer"
                  >
                    <UserPlus className="mr-2 h-4 w-4" />
                    Add {selectedIds.length > 0 ? `${selectedIds.length} ` : ""}Selected
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default function StudentGroups() {
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const { data: groups, isLoading } = useGroups();
  const { data: students } = useStudents();
  const createGroup = useCreateGroup();

  const handleCreate = (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    createGroup.mutate(
      { name: newName.trim() },
      {
        onSuccess: () => {
          setNewName("");
          setCreating(false);
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Student Groups"
        description="Organize students into groups for easy exam assignment"
      >
        <Button
          onClick={() => setCreating((v) => !v)}
          className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" /> Create Group
        </Button>
      </PageHeader>

      {creating && (
        <Card className="glass">
          <CardContent className="pt-4">
            <form onSubmit={handleCreate} className="flex items-center gap-3">
              <Input
                autoFocus
                placeholder="Group name..."
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="max-w-sm"
              />
              <Button type="submit" disabled={!newName.trim() || createGroup.isPending} className="cursor-pointer">
                Save
              </Button>
              <Button type="button" variant="ghost" onClick={() => { setCreating(false); setNewName(""); }}>
                Cancel
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <Card className="glass">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 rounded" />)}
            </div>
          ) : !groups || groups.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
              <div className="rounded-2xl bg-primary/10 p-5">
                <Users className="h-10 w-10 text-primary" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-lg">No groups yet</h3>
                <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                  Create groups to assign students to exam sessions in bulk.
                </p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {groups.map((group) => (
                <GroupRow key={group.id} group={group} students={students} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
