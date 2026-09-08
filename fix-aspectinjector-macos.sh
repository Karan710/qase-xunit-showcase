#!/usr/bin/env bash
# Workaround for pamidur/aspect-injector#210 (open, unresolved as of writing):
# https://github.com/pamidur/aspect-injector/issues/210
#
# On Apple Silicon Macs, AspectInjector's native osx-arm64 build-time binary
# isn't code-signed. macOS Gatekeeper SIGKILLs unsigned ARM64 binaries,
# which surfaces in `dotnet build` as:
#   AspectInjector : error AI_FAIL: Aspect Injector processing has failed.
# with the real cause ("Killed: 9") only visible via `dotnet build -v:diag`.
#
# This ad-hoc self-signs the binary so Gatekeeper allows it to run.
# NOTE: you must re-run this after any `dotnet nuget locals all --clear`
# or if NuGet re-resolves a different AspectInjector version, since the
# binary gets re-extracted fresh each time and loses the signature.

set -euo pipefail

BINARY=$(find "$HOME/.nuget/packages/aspectinjector" \
  -type f -path "*osx-arm64*" -name "AspectInjector" 2>/dev/null | head -n 1)

if [ -z "$BINARY" ]; then
  echo "Could not find the AspectInjector osx-arm64 binary under ~/.nuget/packages/aspectinjector"
  echo "Run 'dotnet restore' first so NuGet has downloaded the package."
  exit 1
fi

echo "Found: $BINARY"
codesign -s - --force --deep "$BINARY"
echo "Signed. Now run: dotnet build"
