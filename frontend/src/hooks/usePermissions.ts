/**
 * Permission hook for RBAC permission checking.
 *
 * Provides functions to check user permissions and roles.
 * Permissions are fetched on auth and cached.
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from './useAuth';
import { rbacApi, Permission } from '@/lib/rbac-api';

interface PermissionState {
  permissions: Permission[];
  roles: string[];
  isLoading: boolean;
  error: string | null;
}

interface UsePermissionsReturn extends PermissionState {
  hasPermission: (resource: string, action: string, scope?: string) => boolean;
  hasAnyPermission: (
    checks: Array<{ resource: string; action: string; scope?: string }>
  ) => boolean;
  hasAllPermissions: (
    checks: Array<{ resource: string; action: string; scope?: string }>
  ) => boolean;
  hasRole: (roleName: string) => boolean;
  hasAnyRole: (roleNames: string[]) => boolean;
  isAdmin: () => boolean;
  isSuperAdmin: () => boolean;
  refetch: () => Promise<void>;
}

export function usePermissions(): UsePermissionsReturn {
  const { isAuthenticated, user } = useAuth();
  const [state, setState] = useState<PermissionState>({
    permissions: [],
    roles: [],
    isLoading: false,
    error: null,
  });

  const fetchPermissions = useCallback(async () => {
    if (!isAuthenticated) {
      setState({
        permissions: [],
        roles: [],
        isLoading: false,
        error: null,
      });
      return;
    }

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await rbacApi.getMyPermissions();
      setState({
        permissions: data.permissions,
        roles: data.roles,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch permissions',
      }));
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchPermissions();
  }, [fetchPermissions, user?.id]);

  const hasPermission = useCallback(
    (resource: string, action: string, scope?: string): boolean => {
      // Super admin has all permissions
      if (state.roles.includes('Super Admin')) {
        return true;
      }

      return state.permissions.some((p) => {
        // Check for wildcard permission
        if (p.resource === '*' && p.action === '*') {
          return true;
        }

        // Check for resource wildcard
        if (p.resource === resource && p.action === '*') {
          return true;
        }

        // Check exact match
        const resourceMatch = p.resource === resource;
        const actionMatch = p.action === action;

        if (!resourceMatch || !actionMatch) {
          return false;
        }

        // If scope is specified, check scope hierarchy
        if (scope) {
          const scopeHierarchy = ['own', 'team', 'all'];
          const requiredScopeIndex = scopeHierarchy.indexOf(scope);
          const userScopeIndex = scopeHierarchy.indexOf(p.scope);

          // User's scope must be >= required scope
          return userScopeIndex >= requiredScopeIndex;
        }

        return true;
      });
    },
    [state.permissions, state.roles]
  );

  const hasAnyPermission = useCallback(
    (checks: Array<{ resource: string; action: string; scope?: string }>): boolean => {
      return checks.some((check) =>
        hasPermission(check.resource, check.action, check.scope)
      );
    },
    [hasPermission]
  );

  const hasAllPermissions = useCallback(
    (checks: Array<{ resource: string; action: string; scope?: string }>): boolean => {
      return checks.every((check) =>
        hasPermission(check.resource, check.action, check.scope)
      );
    },
    [hasPermission]
  );

  const hasRole = useCallback(
    (roleName: string): boolean => {
      return state.roles.includes(roleName);
    },
    [state.roles]
  );

  const hasAnyRole = useCallback(
    (roleNames: string[]): boolean => {
      return roleNames.some((role) => state.roles.includes(role));
    },
    [state.roles]
  );

  const isAdmin = useCallback((): boolean => {
    return hasAnyRole(['Admin', 'Super Admin']);
  }, [hasAnyRole]);

  const isSuperAdmin = useCallback((): boolean => {
    return hasRole('Super Admin');
  }, [hasRole]);

  return useMemo(
    () => ({
      ...state,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      hasRole,
      hasAnyRole,
      isAdmin,
      isSuperAdmin,
      refetch: fetchPermissions,
    }),
    [
      state,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      hasRole,
      hasAnyRole,
      isAdmin,
      isSuperAdmin,
      fetchPermissions,
    ]
  );
}

export default usePermissions;
