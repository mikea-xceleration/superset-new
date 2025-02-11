import {ChartPlugin, ChartProps, SupersetTheme} from "@superset-ui/core";
import React from "react";

declare module '@emotion/react' {
    export interface Theme extends SupersetTheme {}
}

// declare module '@superset-ui/plugin-chart-table' {
//     export interface TableChartProps extends ChartProps {
//         data: Record<string, any>[];
//         height: number;
//         width: number;
//         columnConfigs?: Record<string, any>;
//         tableColumns?: Array<{
//             id: string;
//             Header: string;
//             accessor: string;
//         }>;
//     }
//
//     // Define the static Chart component type
//     export const Chart: React.ComponentType<TableChartProps>;
//
//     // Define the plugin class
//     export default interface TableChartPlugin extends ChartPlugin<any, TableChartProps> {
//         Chart: typeof Chart;
//     }
//
//     const TableChartPluginClass: {
//         new (): TableChartPlugin;
//         Chart: typeof Chart;
//     };
//
//     export default TableChartPluginClass;
// }

