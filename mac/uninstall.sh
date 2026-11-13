#!/bin/bash
for f in com.moy-agent.sutrin com.moy-agent.poshta; do
  launchctl bootout "gui/$(id -u)/$f" 2>/dev/null || true
  rm -f "$HOME/Library/LaunchAgents/$f.plist"
done
echo "Будилките са изключени."
