#!/bin/sh
# Medium-tier eval runner: sh evals/run.sh [--case <name>] [--runs N]
unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE GIT_OBJECT_DIRECTORY GIT_COMMON_DIR
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
runs=3
only=

while [ $# -gt 0 ]; do
  case "$1" in
    --case) [ $# -ge 2 ] || { echo "usage: run.sh [--case <name>] [--runs N]" >&2; exit 2; }
            only=$2; shift 2 ;;
    --runs) [ $# -ge 2 ] || { echo "usage: run.sh [--case <name>] [--runs N]" >&2; exit 2; }
            runs=$2; shift 2 ;;
    *) echo "usage: run.sh [--case <name>] [--runs N]" >&2; exit 2 ;;
  esac
done

cmd=${SLIMSPEC_EVAL_CMD:-"claude -p --plugin-dir $root/plugin --output-format stream-json --verbose --allowedTools Read,Glob,Grep,Write,Edit,Agent,Skill,Bash"}
stamp=$(date -u +%Y-%m-%dT%H-%M-%S)
results=$here/results/$stamp
mkdir -p "$results"

for dir in "$here"/cases/*/; do
  case=$(basename "$dir")
  [ -n "$only" ] && [ "$only" != "$case" ] && continue
  i=1
  while [ "$i" -le "$runs" ]; do
    out=$results/$case/$i
    mkdir -p "$out"
    sandbox=$(mktemp -d)
    cp -R "$here/fixture/." "$sandbox/"
    [ -d "$dir/seed" ] && cp -R "$dir/seed/." "$sandbox/"
    (
      cd "$sandbox" || exit 1
      git init -q
      git add -A
      git -c user.name=eval -c user.email=eval@example.com commit -q -m initial
      # shellcheck disable=SC2086
      $cmd "$(cat "$dir/prompt.md")" > "$out/stdout.log" 2> "$out/stderr.log"
    )
    python3 "$dir/check.py" "$sandbox" "$out/stdout.log" > "$out/check.json" 2> "$out/check.err"
    echo "$sandbox" > "$out/sandbox.txt"
    i=$((i + 1))
  done
done

python3 "$here/verdict.py" "$results"
