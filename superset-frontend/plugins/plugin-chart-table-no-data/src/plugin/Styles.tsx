import { styled } from '@superset-ui/core';

export const EmptyStateContainer = styled.div`
  &.dt-empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    padding: ${({ theme }) => theme.gridUnit * 4}px;
    color: ${({ theme }) => theme.colors.grayscale.base};
    font-size: ${({ theme }) => theme.typography.sizes.m}px;
  }
`;
