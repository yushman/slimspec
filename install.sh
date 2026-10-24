#!/bin/sh
# slimspec installer for OpenCode, Codex and ZCode. Claude Code installs from the marketplace.
set -eu

version=0.1.8
usage='usage: install.sh opencode|codex|zcode|all [--project] [--version <tag>] [--uninstall]'
roles='scanner debugger planner implementer reviewer grounder'

die() { echo "$usage" >&2; exit 2; }

target=
project=
uninstall=
tag=v$version
while [ $# -gt 0 ]; do
  case $1 in
    opencode | codex | zcode | all) [ -z "$target" ] || die; target=$1 ;;
    --project) project=1 ;;
    --uninstall) uninstall=1 ;;
    --version) [ $# -gt 1 ] || die; tag=$2; shift ;;
    *) die ;;
  esac
  shift
done
[ -n "$target" ] || die

want() { [ "$target" = all ] || [ "$target" = "$1" ]; }

if [ -n "$project" ]; then
  if [ "$target" = zcode ]; then
    echo "install.sh: zcode supports global install only" >&2
    exit 2
  fi
  base=$(pwd)
  DATA=$base/.slimspec/install
  OC_AGENTS=$base/.opencode/agents
  CX_AGENTS=$base/.codex/agents
  SHARED=$base/.agents/skills/slimspec
  if [ "$target" = all ]; then
    echo "install.sh: skipping zcode (global install only)" >&2
    target=both
  fi
else
  DATA=${XDG_DATA_HOME:-$HOME/.local/share}/slimspec
  OC_AGENTS=$HOME/.config/opencode/agents
  CX_AGENTS=$HOME/.codex/agents
  SHARED=$HOME/.agents/skills/slimspec
fi
ZC_SKILL=$HOME/.zcode/skills/slimspec
ZC_AGENTS=$HOME/.zcode/agents

if [ "$target" = both ]; then
  want() { [ "$1" != zcode ]; }
fi

has() { for f in "$@"; do [ -e "$f" ] && return 0; done; return 1; }

if [ -n "$uninstall" ]; then
  if want opencode; then
    for r in $roles; do rm -f "$OC_AGENTS/slimspec-$r.md"; done
  fi
  if want codex; then
    for r in $roles; do rm -f "$CX_AGENTS/slimspec-$r.toml"; done
  fi
  if want zcode; then
    if [ -f "$ZC_SKILL/SKILL.md" ] && grep -qF "$DATA" "$ZC_SKILL/SKILL.md"; then
      rm -rf "$ZC_SKILL"
    fi
    for r in $roles; do rm -f "$ZC_AGENTS/slimspec-$r.md"; done
  fi
  if ! has "$OC_AGENTS"/slimspec-*.md "$CX_AGENTS"/slimspec-*.toml; then
    if [ -f "$SHARED/SKILL.md" ] && grep -qF "$DATA" "$SHARED/SKILL.md"; then
      rm -rf "$SHARED"
    fi
    zc_stub=
    if [ -f "$ZC_SKILL/SKILL.md" ] && grep -qF "$DATA" "$ZC_SKILL/SKILL.md"; then zc_stub=$ZC_SKILL; fi
    if [ -n "$project" ] || ! has ${zc_stub:+"$zc_stub"} "$ZC_AGENTS"/slimspec-*.md; then
      rm -rf "$DATA"
    fi
  fi
  exit 0
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

curl -fsSL "https://github.com/yushman/slimspec/archive/refs/tags/$tag.tar.gz" -o "$TMP/src.tgz"
mkdir "$TMP/src"
tar -xzf "$TMP/src.tgz" -C "$TMP/src" --strip-components=1
for p in plugin/skills plugin/agents hosts/skill/SKILL.md; do
  [ -e "$TMP/src/$p" ] || { echo "install.sh: $tag has no $p" >&2; exit 1; }
done

esc=$(printf '%s' "$DATA" | sed 's/[\\&|]/\\&/g')
put() { sed "s|<root>|$esc|g" "$1" > "$2"; }

mkdir -p "$DATA"
rm -rf "$DATA/skills" "$DATA/agents" "$DATA/hosts"
mkdir "$DATA/hosts"
cp -R "$TMP/src/plugin/skills" "$TMP/src/plugin/agents" "$DATA/"
cp "$TMP/src/hosts"/*.md "$DATA/hosts/"

if want opencode || want codex; then
  mkdir -p "$SHARED"
  put "$TMP/src/hosts/skill/SKILL.md" "$SHARED/SKILL.md"
fi
if want opencode; then
  mkdir -p "$OC_AGENTS"
  for r in $roles; do put "$TMP/src/hosts/opencode/agents/slimspec-$r.md" "$OC_AGENTS/slimspec-$r.md"; done
fi
if want codex; then
  mkdir -p "$CX_AGENTS"
  for r in $roles; do put "$TMP/src/hosts/codex/agents/slimspec-$r.toml" "$CX_AGENTS/slimspec-$r.toml"; done
fi
if want zcode; then
  mkdir -p "$ZC_SKILL" "$ZC_AGENTS"
  put "$TMP/src/hosts/skill/SKILL.md" "$ZC_SKILL/SKILL.md"
  for r in $roles; do put "$TMP/src/hosts/zcode/agents/slimspec-$r.md" "$ZC_AGENTS/slimspec-$r.md"; done
fi

if [ -n "$project" ]; then
  touch .gitignore
  ignore() {
    grep -qxF "$1" .gitignore && return 0
    [ -z "$(tail -c1 .gitignore)" ] || echo >> .gitignore
    echo "$1" >> .gitignore
  }
  ignore .slimspec/install/
  if want opencode || want codex; then ignore .agents/skills/slimspec/; fi
  if want opencode; then ignore '.opencode/agents/slimspec-*'; fi
  if want codex; then ignore '.codex/agents/slimspec-*'; fi
fi
