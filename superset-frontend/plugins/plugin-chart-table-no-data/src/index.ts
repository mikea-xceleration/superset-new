import TableChartPlugin from '@superset-ui/plugin-chart-table';
import { Behavior, ChartMetadata, t } from '@superset-ui/core';
import thumbnail from './images/thumbnail.png';

const metadata = new ChartMetadata({
  behaviors: [Behavior.InteractiveChart],
  category: t('Table'),
  description: t('Table with empty state handling'),
  name: t('Table with Empty State'),
  thumbnail,
  tags: [t('Tabular'), t('Report')],
});

export default class TableNoDataPlugin extends TableChartPlugin {
  constructor() {
    super();
    this.metadata = metadata;

    this.loadChart = () => import('./plugin/components/EmptyStateTable')
      .then(module => module.default);
  }
}
