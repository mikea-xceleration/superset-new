import {TableChartTransformedProps} from '@superset-ui/plugin-chart-table';
import {ChartProps, QueryFormData} from '@superset-ui/core';

export interface EmptyStateFormData extends QueryFormData {
    empty_state_message?: string;
}

// Extend TableChartTransformedProps to add our custom property
export interface EmptyStateProps extends ChartProps<EmptyStateFormData>, TableChartTransformedProps {
    emptyStateMessage?: string;
}