"use client";

import { useState, useCallback } from "react";
import { api, isSuccess } from "@/lib/api";
import type { ProfileData, PasswordChangeData } from "@/types";

interface UserTool {
  id: number;
  name: string;
  display_name: string;
  description: string;
  route: string;
}

interface UseProfileReturn {
  isLoading: boolean;
  error: string | null;
  getProfile: () => Promise<ProfileData | null>;
  updateProfile: (data: ProfileData) => Promise<boolean>;
  changePassword: (data: PasswordChangeData) => Promise<boolean>;
  getUserTools: () => Promise<UserTool[]>;
  clearError: () => void;
}

export function useProfile(): UseProfileReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getProfile = useCallback(async (): Promise<ProfileData | null> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await api.get<{ profile: ProfileData }>("/user/profile");

      if (isSuccess(response)) {
        return response.data.profile;
      } else {
        setError(response.message || "Failed to fetch profile");
        return null;
      }
    } catch {
      setError("Network error. Please try again.");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(
    async (data: ProfileData): Promise<boolean> => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await api.put("/user/profile", data);

        if (isSuccess(response)) {
          return true;
        } else {
          setError(response.message || "Failed to update profile");
          return false;
        }
      } catch {
        setError("Network error. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const changePassword = useCallback(
    async (data: PasswordChangeData): Promise<boolean> => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await api.post("/user/change-password", {
          current_password: data.currentPassword,
          new_password: data.newPassword,
        });

        if (isSuccess(response)) {
          return true;
        } else {
          setError(response.message || "Failed to change password");
          return false;
        }
      } catch {
        setError("Network error. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const getUserTools = useCallback(async (): Promise<UserTool[]> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await api.get<{ tools: UserTool[] }>("/user/tools");

      if (isSuccess(response)) {
        return response.data.tools;
      } else {
        setError(response.message || "Failed to fetch tools");
        return [];
      }
    } catch {
      setError("Network error. Please try again.");
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    getProfile,
    updateProfile,
    changePassword,
    getUserTools,
    clearError,
  };
}
