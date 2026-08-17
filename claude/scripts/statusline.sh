#!/usr/bin/env bash
# Claude Code status line: model, rate limits, context, cost
input=$(cat)

# Helper: format seconds into countdown
format_reset() {
  local diff=$(( $1 - $(date +%s) ))
  if [ "$diff" -le 0 ]; then echo "now"; return; fi
  local d=$(( diff / 86400 )) h=$(( (diff % 86400) / 3600 )) m=$(( (diff % 3600) / 60 ))
  if [ "$d" -gt 0 ]; then printf "%dd %dh" "$d" "$h"
  elif [ "$h" -gt 0 ]; then printf "%dh %dm" "$h" "$m"
  else printf "%dm" "$m"
  fi
}

out=""
add() { [ -n "$out" ] && out="$out | "; out="${out}$1"; }

# Mode (set by the Claude launchers in agents-modes via the mode settings file's env)
[ -n "${AGENTS_CLAUDE_MODE:-}" ] && add "[$AGENTS_CLAUDE_MODE]"

# Model
model=$(echo "$input" | jq -r '.model.display_name // empty')
[ -n "$model" ] && add "$model"

# 5-hour rate limit
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
if [ -n "$five_pct" ]; then
  s="5h: $(printf "%.0f" "$five_pct")%"
  five_at=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
  [ -n "$five_at" ] && s="$s ($(format_reset "$five_at"))"
  add "$s"
fi

# 7-day rate limit
week_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
if [ -n "$week_pct" ]; then
  s="7d: $(printf "%.0f" "$week_pct")%"
  week_at=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
  [ -n "$week_at" ] && s="$s ($(format_reset "$week_at"))"
  add "$s"
fi

# Context window
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
[ -n "$ctx_pct" ] && add "ctx: $(printf "%.0f" "$ctx_pct")%"

[ -n "$out" ] && printf "%s" "$out"
