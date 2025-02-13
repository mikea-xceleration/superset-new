// src/types.ts
import {
  TableChartProps,
} from '@superset-ui/plugin-chart-table';

export interface EmptyStateTableProps extends TableChartProps
{
  emptyStateMessage?: string;
}

// Re-export base table types for convenience
export { TableChartProps };
