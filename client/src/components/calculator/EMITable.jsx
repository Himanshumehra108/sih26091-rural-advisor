import React from 'react';

export default function EMITable({ rows = [] }) {
  return <table><tbody>{rows.map((row) => <tr key={row.id}><td>{row.label}</td><td>{row.value}</td></tr>)}</tbody></table>;
}
