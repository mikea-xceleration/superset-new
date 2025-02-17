import React, { Suspense } from 'react';
import {EmptyStateContainer} from '../Styles';
import {  EmptyStateTableTransformedProps } from '../../types';
import TableChartPlugin from '@superset-ui/plugin-chart-table';

// Lazy load the base chart
const BaseChart = React.lazy(async () => {
  const basePlugin = new TableChartPlugin();
  const loadChart = basePlugin.loadChart();
  const Component = await loadChart;
  return {default: Component};
});

const  EmptyStateTable: React.FC<EmptyStateTableTransformedProps> = props =>{
  const { isEmpty, emptyStateMessage, ...rest } = props;
 
  
  if (isEmpty) {
    return (
      <EmptyStateContainer className="dt-empty-state">
        {emptyStateMessage || 'No results found'}
      </EmptyStateContainer>
    );    
  }
  return (
    <Suspense fallback={<div></div>}>
      <BaseChart {...rest} />
    </Suspense>
  );
};

EmptyStateTable.displayName = 'EmptyStateTable';
export default EmptyStateTable;
