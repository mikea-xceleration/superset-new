import React, { Suspense } from 'react';
import {EmptyStateContainer} from '../Styles';
import { EmptyStateTableProps } from '../../types';
import TableChartPlugin from '@superset-ui/plugin-chart-table';

// Lazy load the base chart
const BaseChart = React.lazy(async () => {
  const basePlugin = new TableChartPlugin();
  const loadChart = basePlugin.loadChart();
  const Component = await loadChart;
  return {default: Component};
});

const  EmptyStateTable: React.FC<EmptyStateTableProps> = props =>{
  const { queriesData, ...rest } = props;
  const response = queriesData[0];
 
  const hasNoData = !response?.data || response.data.length === 0;
  
  if (hasNoData) {
    return (
      <EmptyStateContainer className="dt-empty-state">
        {rest.formData?.empty_state_message || 'No results found'}
      </EmptyStateContainer>
    );    
  }
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <BaseChart {...rest} queriesData={queriesData} />
    </Suspense>
  );
};

EmptyStateTable.displayName = 'EmptyStateTable';
export default EmptyStateTable;
