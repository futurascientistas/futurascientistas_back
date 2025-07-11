'use client';
import { useEffect, useState } from 'react';
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { fetchGroups, Group } from "@/services/default-groups";

type Props = {
  value?: string;
  onChange: (value: string) => void;
};

export default function GroupSelect({ value, onChange }: Props) {
  const [groups, setGroups] = useState<Group[]>([]);

  function capitalizeFirst(text: string) {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  useEffect(() => {
    fetchGroups()
      .then(setGroups)
      .catch(err => console.error("Erro ao carregar grupos:", err));
  }, []);

  return (
    <div>
      <Label htmlFor="group" className="text-sm font-medium">
        Você é...
      </Label>
      <Select onValueChange={onChange} defaultValue={value}>
        <SelectTrigger className="w-full mt-1">
          <SelectValue placeholder="Selecione">
            {value ? capitalizeFirst(groups.find(g => String(g.name) === value)?.name || "Selecione") : "Selecione"}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {groups.map(group => (
            <SelectItem key={group.name} value={group.name}>
              {capitalizeFirst(group.name)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
