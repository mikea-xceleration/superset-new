// src/types.ts
import { TableChartFormData, TableChartProps, TableChartTransformedProps } from '@superset-ui/plugin-chart-table';

export interface EmptyStateTableProps extends TableChartProps {
  rawFormData: EmptyStateTableChartFormData
}

export type EmptyStateTableChartFormData = TableChartFormData & {
  empty_state_message?: string;
}

export interface EmptyStateTableTransformedProps extends TableChartTransformedProps {
  isEmpty: boolean;
  emptyStateMessage?: string;
}

// Re-export base table types for convenience
export { TableChartProps, TableChartTransformedProps };
