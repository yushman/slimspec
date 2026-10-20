# Prompt-debate checklist

1. Questions to the user go through `AskUserQuestion`.
2. One decision per question, 2-4 options, recommendation first; independent questions batched up to 4 (D6, D23).
3. Explore asks about open decisions instead of deciding them.
4. Gates show a walkthrough and wait for the user (D22).
5. Agents never decide for the user; BLOCKED questions surface and the agent is relaunched with the answers (D3).
6. Agent YAML and diffs stay out of chat (D4).
7. Escalation to the user after 2 fix cycles (D9).
8. DESIGN decisions change before behavior.
