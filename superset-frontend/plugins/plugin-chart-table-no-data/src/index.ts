import { Behavior, ChartMetadata, ChartPlugin, t } from '@superset-ui/core';
import controlPanel from './plugin/controlPanel';
import thumbnail from './images/thumbnail.png';
import { EmptyStateTableChartFormData, EmptyStateTableProps } from './types';
import transformProps from './plugin/transformProps';
import { BasePluginUtils } from './plugin/utils/BasePluginUtils';
import buildQuery from './plugin/buildQuery';

const metadata = new ChartMetadata({
  behaviors: [Behavior.InteractiveChart],
  category: t('Table'),
  description: t('Table with empty state handling'),
  name: t('Table with Empty State'),
  thumbnail,
  tags: [t('Tabular'), t('Report')],
  enableNoResults: false
});
export default class TableNoDataPlugin extends ChartPlugin<
  EmptyStateTableChartFormData,
  EmptyStateTableProps
> {
  constructor() {
    BasePluginUtils.Initialize();
    super({
      loadChart: () => import('./plugin/components/EmptyStateTable'),
      metadata,
      // transformProps,
      loadTransformProps: () => chartProps =>{
        return transformProps(chartProps);
      },
      controlPanel,
      buildQuery: buildQuery,
    });
  }
}


