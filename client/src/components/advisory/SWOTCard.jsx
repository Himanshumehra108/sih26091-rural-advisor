import React from 'react';

export default function SWOTCard({ title, items = [] }) {
  return <section><h2>{title}</h2><ul>{items.map((item) => <li key={item}>{item}</li>)}</ul></section>;
}
