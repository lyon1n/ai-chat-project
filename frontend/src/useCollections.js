import { useCallback, useEffect, useState } from "react";
import { apiFetch, errorMessage } from "./api";

export function useCollections() {
  const [collections, setCollections] = useState([]);
  const [currentCollection, setCurrentCollection] = useState("");
  const [error, setError] = useState("");

  const refreshCollections = useCallback(async () => {
    try {
      const res = await apiFetch("/collections");
      if (!res.ok) throw new Error(await errorMessage(res, "获取知识库失败"));
      const data = await res.json();
      setCollections(data.collections || []);
      setError("");
    } catch (err) {
      setCollections([]);
      setError(err.message || "获取知识库失败");
    }
  }, []);

  const deleteCollection = useCallback(async (name) => {
    const res = await apiFetch(`/collections/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      throw new Error(await errorMessage(res, "删除失败"));
    }
    await refreshCollections();
  }, [refreshCollections]);

  useEffect(() => {
    refreshCollections();
  }, [refreshCollections]);

  return {
    collections,
    currentCollection,
    setCurrentCollection,
    refreshCollections,
    deleteCollection,
    collectionsError: error,
  };
}
