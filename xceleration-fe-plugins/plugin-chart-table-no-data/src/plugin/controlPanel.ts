import { t } from '@superset-ui/core';
import {ControlPanelConfig} from '@superset-ui/chart-controls';

export const controlPanel: ControlPanelConfig = {
    controlPanelSections: [
        {
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
        },
    ],
};