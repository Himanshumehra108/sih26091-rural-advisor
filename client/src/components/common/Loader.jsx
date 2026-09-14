import React from "react";

export default function Loader({ label = "Loading…" }) {
  return (
    <span className="inline-loader" role="status">
      <span className="loader" aria-hidden="true"></span>
      {label}
    </span>
  );
}
