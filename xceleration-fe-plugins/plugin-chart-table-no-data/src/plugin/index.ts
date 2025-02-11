import { buildQueryContext, ChartPlugin, ChartMetadata } from '@superset-ui/core';
import { EmptyStateFormData, EmptyStateProps } from '../types';
import EmptyStateTable from './components/EmptyStateTable';
import { controlPanel } from './controlPanel';

const metadata = new ChartMetadata({
    name: 'Table with Empty State',
    description: 'Table visualization with customizable empty state message',
    thumbnail: '',
    tags: ['table'],
    canBeAnnotationTypes: [],
    credits: [''],
    supportedAnnotationTypes: [],
    useLegacyApi: false,
    behaviors: [],
});

export const createEmptyStatePlugin = () => {
    const plugin = new ChartPlugin<EmptyStateFormData, EmptyStateProps>({
        metadata,
        Chart: EmptyStateTable,
        controlPanel,
        buildQuery: formData => {
            return buildQueryContext(formData, (baseQueryObject) => [{
                ...baseQueryObject,
            }]);
        },
        transformProps: (chartProps) => {
            const { queriesData, formData } = chartProps;
            return {
                ...chartProps,
                emptyStateMessage: (formData as EmptyStateFormData).empty_state_message,
                data: queriesData[0].data,
                // Include other required props from TableChartTransformedProps as needed
                height: chartProps.height,
                width: chartProps.width,
                // Add any other required props from TableChartTransformedProps
            };
        },
    });

    return plugin;
};