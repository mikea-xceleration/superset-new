import {createEmptyStatePlugin} from './plugin';
export const EmptyStateTablePlugin = createEmptyStatePlugin()
EmptyStateTablePlugin.configure({key: 'table-no-data'}).register();
export default EmptyStateTablePlugin;