import { t } from '@superset-ui/core';
import {ControlPanelConfig} from '@superset-ui/chart-controls';
import TableChartPlugin from '@superset-ui/plugin-chart-table'

const emptyStateSection = {
  label: t('Empty State Configuration'),
  expanded: true,
  controlSetRows: [
    [
      {
        name: 'empty_state_message',
        config: {
          type: 'TextAreaControl',
          label: t('Empty State Message'),
          description: t('Message to display when the query returns no results'),
          default: 'No results found',
          language: 'markdown',
          offerEditInModal: true,
          renderTrigger: true,
        },
      },
    ],
  ],
};

const baseControlPanel = new TableChartPlugin().controlPanel;

// Create new control panel by extending the base configuration
const controlPanel: ControlPanelConfig = {
  ...baseControlPanel,
  controlPanelSections: [
    ...baseControlPanel.controlPanelSections,
    emptyStateSection,
  ],
};

export default controlPanel;
