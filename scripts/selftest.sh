#!/usr/bin/env bash
# 校验器自测：scripts/selftest/PASS_*.md 必须 PASS，FAIL_*.md 必须 FAIL。改过 validate_output.py 后跑一遍。
set -u
here="$(cd "$(dirname "$0")" && pwd)"
bad=0
for f in "$here"/selftest/*.md; do
  base="$(basename "$f")"; want="${base%%_*}"
  if python3 -I "$here/validate_output.py" "$f" >/dev/null 2>&1; then got=PASS; else got=FAIL; fi
  if [ "$got" = "$want" ]; then printf 'ok        %s\n' "$base"; else printf 'MISMATCH  %s  (期望 %s，实际 %s)\n' "$base" "$want" "$got"; bad=1; fi
done
[ $bad -eq 0 ] && echo "selftest: all ok" || echo "selftest: FAILED"
exit $bad
