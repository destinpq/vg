'use client';

import React from 'react';
import { Badge, Card } from 'antd';

interface CostBadgeProps {
  totalCost: number;
  apiCallCount: number;
}

export const CostBadge: React.FC<CostBadgeProps> = ({ totalCost, apiCallCount }) => {
  return (
    <div className="cost-badge">
      <Badge.Ribbon 
        text={
          <span className="cost-value">
            ₹{totalCost}
          </span>
        } 
        color="#722ed1"
      >
        <Card className="text-center" style={{ width: 180 }}>
          <div className="cost-card-content">
            <div className="cost-label font-semibold">Total Server Cost</div>
            <div className="cost-label mt-1">{apiCallCount} API calls</div>
          </div>
        </Card>
      </Badge.Ribbon>
    </div>
  );
}; 