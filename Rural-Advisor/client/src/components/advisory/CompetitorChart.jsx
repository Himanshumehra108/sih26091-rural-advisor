import React from 'react';

export default function CompetitorChart({ competitors = [] }) {
  return <ul>{competitors.map((competitor) => <li key={competitor.id ?? competitor.name}>{competitor.name}</li>)}</ul>;
}
