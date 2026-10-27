#!/usr/bin/env bash
# AC checks for the docs migration, run by the integrator after the writers land.
#   bash .scratch/36-docs-migration/work/validate.sh
set -u
cd "${1:-$(git rev-parse --show-toplevel)}" || exit 1

fail=0
say() { printf '%s\n' "$*"; }
bad() { printf 'MISS  %s\n' "$*"; fail=$((fail+1)); }

say "== new files"
for f in docs/0_STAGING.md docs/0_ROADMAP.md docs/1_PROBLEM.md docs/2_GOAL.md \
         docs/3_REQUIREMENT.md docs/4_USECASE.md docs/5_PRODUCT.md docs/6_ARCHITECTURE.md \
         docs/7_INTERFACE.md docs/8_DETAIL.md docs/9_IMPLEMENTATION.md; do
  [ -s "$f" ] && printf 'ok    %6d bytes  %-28s %s\n' "$(wc -c <"$f")" "$f" "$(head -1 "$f")" \
              || bad "$f missing or empty"
done

say
say "== AC2: no dates / rounds / session words / 'as of' in docs"
if grep -rnE '20[0-9]{2}-[0-9]{2}|round [0-9]+|this session|as of ' docs/*.md; then
  bad "dates or session words above"
else
  say "ok    none"
fi

say
say "== AC5: zone order per file (title H1, then EXPLICIT/CONFIRMED/INFERRED in order)"
for f in docs/[1-9]_*.md; do
  zones=$(grep -n '^# ' "$f" | awk '{print $2}' | tr '\n' ' ')
  case "$zones" in
    *"EXPLICIT CONFIRMED INFERRED"*|*"EXPLICIT INFERRED"*|*"CONFIRMED INFERRED"*|*"EXPLICIT CONFIRMED"*|*"INFERRED"*|*"EXPLICIT"*|*"CONFIRMED"*)
      printf 'ok    %-28s %s\n' "$f" "$zones" ;;
    *) bad "$f zone order: $zones" ;;
  esac
  # the title must be the first H1 and must not be a zone name
  first=$(grep -m1 '^# ' "$f")
  if [ "$(grep -nm1 '^#' "$f" | cut -d: -f2 | cut -c1-2)" = "##" ]; then bad "$f opens with an H2 before any zone"; fi
  case "$first" in
    "# EXPLICIT"|"# CONFIRMED"|"# INFERRED") bad "$f starts with a zone, not its title" ;;
  esac
done

say
say "== P-numbers: all 41 must be present in 3_REQUIREMENT.md, none duplicated across docs"
for n in $(seq 1 41); do
  grep -qE "^##+ P$n — " docs/3_REQUIREMENT.md || bad "P$n missing from 3_REQUIREMENT.md"
  others=$(grep -rlE "^##+ P$n — " docs/ | grep -v '^docs/3_REQUIREMENT.md$')
  [ -n "$others" ] && bad "P$n also stated in $others (second home)"
done

say
say "== no old path survives in a live doc"
if grep -rnE 'docs/drawing/|STATUS\.md|WORKSPACE\.md' \
     AGENTS.md README.md docs/*.md 2>/dev/null; then
  bad "live doc still points at docs/drawing/"
else
  say "ok    none"
fi

say
say "== STATUS.md retired, old docs gone"
[ -e STATUS.md ] && bad "STATUS.md still exists"
[ -d docs/drawing ] && bad "docs/drawing still exists"

say
say "failures: $fail"
exit $((fail > 0))
