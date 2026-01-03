/**
 * RequireRole component for conditional rendering based on roles.
 *
 * Usage:
 * <RequireRole role="Admin">
 *   <AdminPanel />
 * </RequireRole>
 *
 * <RequireRole roles={["Admin", "Manager"]}>
 *   <ManagementPanel />
 * </RequireRole>
 */

import React from 'react';
import { usePermissions } from '@/hooks/usePermissions';

interface RequireRoleProps {
  children: React.ReactNode;
  role?: string;
  roles?: string[];
  requireAll?: boolean;
  fallback?: React.ReactNode;
}

export function RequireRole({
  children,
  role,
  roles,
  requireAll = false,
  fallback = null,
}: RequireRoleProps) {
  const { hasRole, hasAnyRole, isLoading, roles: userRoles } = usePermissions();

  if (isLoading) {
    return null;
  }

  let hasAccess = false;

  if (role) {
    hasAccess = hasRole(role);
  } else if (roles) {
    if (requireAll) {
      hasAccess = roles.every((r) => userRoles.includes(r));
    } else {
      hasAccess = hasAnyRole(roles);
    }
  }

  if (hasAccess) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}

export default RequireRole;
