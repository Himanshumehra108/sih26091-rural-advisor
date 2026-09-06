import React from 'react';

export default function MoratoriumTimeline({ milestones = [] }) {
  return <ol>{milestones.map((milestone) => <li key={milestone.id ?? milestone.label}>{milestone.label}</li>)}</ol>;
}
