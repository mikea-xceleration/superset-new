import { jsx, css, Theme } from '@emotion/react';
import React from 'react';
import TableChart from '@superset-ui/plugin-chart-table/lib/TableChart';
import { EmptyStateProps } from "../../types";
import { getChartComponentRegistry } from '@superset-ui/core';

const TableChartComponent = getChartComponentRegistry().get('table');
const emptyStateStyles = (theme: Theme) => css`
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    padding: ${theme.gridUnit * 4}px;
    color: ${theme.colors.grayscale.base};
    font-size: ${theme.typography.sizes.m}px;
`;

const EmptyStateTable: React.FC<EmptyStateProps> = (props) => {
    const { data, emptyStateMessage, ...rest } = props;

    if (!data || data.length === 0) {
        return (
            <div css={theme => emptyStateStyles(theme)}>
                {emptyStateMessage || 'No results found'}
            </div>
        );
    }

    return <TableChart {...props} />;
};

export default EmptyStateTable;