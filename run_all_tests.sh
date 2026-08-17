#!/usr/bin/env bash
# Run every ViridisOS test suite. Green across all = the gate for "done".
set -u
cd "$(dirname "$0")"
pass=0; fail=0
for t in tests/test_*.py; do
  out=$(python3 "$t" 2>&1)
  last=$(echo "$out" | tail -1)
  p=$(echo "$last" | awk '{print $1}')
  f=$(echo "$last" | awk '{print $3}')
  printf "%-34s %s\n" "$(basename "$t")" "$last"
  [ "$f" != "0" ] && echo "$out"
  pass=$((pass + ${p:-0})); fail=$((fail + ${f:-0}))
done
echo "----------------------------------------------"
echo "TOTAL: $pass passed, $fail failed"
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
