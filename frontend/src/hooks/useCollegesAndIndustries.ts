"use client";

import { useEffect, useState } from "react";
import { fetchColleges, fetchIndustries } from "@/lib/api";
import { College, Industry } from "@/lib/types";

export function useCollegesAndIndustries() {
  const [colleges, setColleges] = useState<College[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchColleges(), fetchIndustries()])
      .then(([c, i]) => {
        setColleges(c);
        setIndustries(i);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { colleges, industries, loading, error };
}
