/**
 * CanAccess component for conditional rendering based on permissions.
 *
 * Usage:
 * <CanAccess permission="users:create">
 *   <CreateUserButton />
 * </CanAccess>
 *
 * <CanAccess resource="documents" action="delete" scope="all">
 *   <DeleteAllButton />
 * </CanAccess>
 */

import React from 'react';
import { usePermissions } from '@/hooks/usePermissions';

interface CanAccessProps {
  children: React.ReactNode;
  permission?: string;
  resource?: string;
  action?: string;
  scope?: string;
  fallback?: React.ReactNode;
  any?: Array<{ resource: string; action: string; scope?: string }>;
  all?: Array<{ resource: string; action: string; scope?: string }>;
}

export function CanAccess({
  children,
  permission,
  resource,
  action,
  scope,
  fallback = null,
  any,
  all,
}: CanAccessProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isLoading } =
    usePermissions();

  if (isLoading) {
    return null;
  }

  let hasAccess = false;

  if (permission) {
    const [res, act, scp] = permission.split(':');
    hasAccess = hasPermission(res, act, scp);
  } else if (resource && action) {
    hasAccess = hasPermission(resource, action, scope);
  } else if (any) {
    hasAccess = hasAnyPermission(any);
  } else if (all) {
    hasAccess = hasAllPermissions(all);
  }

  if (hasAccess) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}

export default CanAccess;
