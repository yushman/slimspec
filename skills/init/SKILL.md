---
name: init
description: "Tell the user how to run the optional slimspec config wizard."
disable-model-invocation: true
---

The config is optional: every key has a default. Do not run the wizard yourself, it is interactive.

1. If `.slimspec/config.yaml` exists, show its contents first.
2. Reply with one short message: to create or change the config, run this from the project root in your own terminal:

```
bash "${CLAUDE_PLUGIN_ROOT}/scripts/init.sh"
```
