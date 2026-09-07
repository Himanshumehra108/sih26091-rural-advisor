import React from 'react';

export default function SchemeCard({ name, amount }) {
  return <article><h2>{name}</h2><p>{amount}</p></article>;
}
