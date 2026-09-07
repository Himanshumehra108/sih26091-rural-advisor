import { useMemo } from 'react';

export default function useSchemeCalc(capital = 0) {
  return useMemo(() => ({ capital: Number(capital) || 0, schemes: [] }), [capital]);
}
