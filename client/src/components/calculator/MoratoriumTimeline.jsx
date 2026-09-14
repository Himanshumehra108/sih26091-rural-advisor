import React from "react";

// Simple segmented bar showing how many quarters are moratorium
// (interest-only / deferred) vs active repayment — derived straight
// from the emi-schedule response's moratorium_quarters / repayment_quarters.
export default function MoratoriumTimeline({ moratoriumQuarters = 0, repaymentQuarters = 0 }) {
  const total = moratoriumQuarters + repaymentQuarters || 1;
  const moratoriumPct = (moratoriumQuarters / total) * 100;

  return (
    <div className="moratorium-timeline">
      <div className="timeline-bar">
        {moratoriumQuarters > 0 && (
          <div className="timeline-segment moratorium" style={{ width: `${moratoriumPct}%` }}>
            {moratoriumQuarters}Q
          </div>
        )}
        <div className="timeline-segment repayment" style={{ width: `${100 - moratoriumPct}%` }}>
          {repaymentQuarters}Q
        </div>
      </div>
      <div className="timeline-legend">
        <span><i className="dot moratorium" /> Moratorium ({moratoriumQuarters} quarters)</span>
        <span><i className="dot repayment" /> Repayment ({repaymentQuarters} quarters)</span>
      </div>
    </div>
  );
}
