// Session storage restoration is an explicit client-only hydration step.
import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import nextTypescript from 'eslint-config-next/typescript';
export default defineConfig([...nextVitals, ...nextTypescript, { rules: { 'react-hooks/set-state-in-effect': 'off' } }, globalIgnores(['.next/**', 'next-env.d.ts'])]);
