// Must stay identical to normalize_identifier() in pipeline/models.py,
// because the alias map in muni.json is keyed by its output.
export function normalizeIdentifier(value: string): string {
  return value.toLowerCase().replace(/by-?law/g, 'bylaw').replace(/[\s\-_.]/g, '');
}

// Shapes of official numbers (plan §6.1). When the input looks like one of these
// and isn't in the alias map, we say "no match" instead of fuzzy-guessing a matter.
const IDENTIFIER_PATTERNS = [
  /^by-?\s*law\s*(no\.?\s*)?\d{2,4}[\s-]*\d{2,3}$/i, // By-law 2025-086, bylaw 2025 086
  /^[a-z]{2,5}\s*\d{4}[\s-]*\d{3}(\.\d)?$/i, // COM2025-034
  /^z[\s-]*\d{2}[\s-]*\d{2}$/i, // Z-24-05
  /^opa\s*(no\.?\s*)?\d+$/i, // OPA 12
  /^md\s*(no\.?\s*)?\d+[\s-]*\d*$/i, // MD 2025-01
];

export function looksLikeIdentifier(value: string): boolean {
  const trimmed = value.trim();
  return IDENTIFIER_PATTERNS.some((pattern) => pattern.test(trimmed));
}
