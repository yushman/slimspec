#!/bin/bash
# Optional slimspec config wizard. Run from the project root: bash scripts/init.sh

CONFIG=.slimspec/config.yaml

# ask VAR "prompt" "default": read a line into VAR, Enter keeps the default
ask() {
  printf '%s [%s]: ' "$2" "$3"
  IFS= read -r line || { echo; echo "aborted" >&2; exit 1; }
  eval "$1=\${line:-\$3}"
}

# choice VAR "prompt" "a b c" "default": ask until the answer is one of the options
choice() {
  while :; do
    ask "$1" "$2 ($3)" "$4"
    eval "val=\$$1"
    case " $3 " in *" $val "*) return ;; esac
    echo "  invalid: choose one of: $3"
  done
}

# yesno VAR "prompt" "y|n"
yesno() {
  while :; do
    ask "$1" "$2 (y/n)" "$3"
    eval "val=\$$1"
    case "$val" in y|Y|yes) eval "$1=y"; return ;; n|N|no) eval "$1=n"; return ;; esac
    echo "  invalid: answer y or n"
  done
}

# line KEY_AND_VALUE "comment": one YAML line with an aligned comment
line() { printf '%-26s# %s\n' "$1" "$2"; }

detect_test() {
  if [ -f package.json ] && grep -q '"test"' package.json; then echo "npm test"
  elif [ -f Makefile ] && grep -q '^test:' Makefile; then echo "make test"
  elif [ -f gradlew ]; then echo "./gradlew test"
  elif [ -f Cargo.toml ]; then echo "cargo test"
  elif [ -f go.mod ]; then echo "go test ./..."
  elif [ -f pyproject.toml ] || [ -f pytest.ini ]; then echo "pytest"
  fi
}

if [ -f "$CONFIG" ]; then
  yesno overwrite "$CONFIG exists. Overwrite?" n
  [ "$overwrite" = y ] || { echo "kept existing config"; exit 0; }
fi

choice mode "mode" "fast medium full" medium

choice format "spec.format" "claude-md readme central native none" claude-md
unit=auto
adr=n
if [ "$format" != none ]; then
  ask unit "spec.unit (auto or a dir glob, e.g. src/*/)" auto
  yesno adr "spec.adr: also keep decisions in docs/adr/" n
fi

detected=$(detect_test)
if [ -n "$detected" ]; then
  ask test "test (auto, 1 = $detected, or type a command)" auto
  [ "$test" = 1 ] && test=$detected
else
  ask test "test (auto or type a command)" auto
fi

choice commit "commit" "none lane wave" none

while :; do
  ask agents "apply.agents (max parallel implementers, integer >= 1)" 3
  case "$agents" in ''|*[!0-9]*|0*) ;; *) break ;; esac
  echo "  invalid: enter an integer >= 1"
done
choice depth "review.depth" "auto low medium high" auto

models=""
yesno override "Override models per role?" n
if [ "$override" = y ]; then
  for role in scanner planner implementer reviewer grounder; do
    ask m "models.$role (empty = agent default)" ""
    [ -n "$m" ] && models="$models  $role: $m
"
  done
fi

quote() { if [ "$1" = auto ]; then printf auto; else printf '"%s"' "$1"; fi; }

yaml=$(
  line "mode: $mode" "fast | medium | full"
  echo "spec:"
  line "  format: $format" "claude-md | readme | central | native | none"
  line "  unit: $(quote "$unit")" 'auto (by build files) | dir glob, e.g. "src/*/"'
  if [ "$adr" = y ]; then adr=true; else adr=false; fi
  line "  adr: $adr" "also keep decisions in docs/adr/NNNN-*.md"
  line "test: $(quote "$test")" "auto | an explicit command"
  line "commit: $commit" "none | lane | wave"
  echo "apply:"
  line "  agents: $agents" "max parallel implementers = max lanes per wave"
  echo "review:"
  line "  depth: $depth" "auto (by mode) | low | medium | high"
  if [ -n "$models" ]; then
    echo "models:                   # per-role overrides: scanner, planner, implementer, reviewer, grounder"
    printf '%s' "$models"
  else
    line "models: {}" "per-role overrides: scanner, planner, implementer, reviewer, grounder"
  fi
)

echo
echo "$CONFIG:"
echo "$yaml"
echo
yesno ok "Write it?" y
[ "$ok" = y ] || { echo "nothing written"; exit 0; }

mkdir -p .slimspec
echo "$yaml" > "$CONFIG"
echo "wrote $CONFIG"
