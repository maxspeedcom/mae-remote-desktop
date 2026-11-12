#!/bin/bash
# Build the MAE Remote source tree for an upstream release: ./update-upstream.sh <upstream-tag>   (e.g. 1.5.3)
# 1) export the upstream tag with libs/hbb_common vendored (no submodule)
# 2) drop what MAE does not ship: the submodule pointer, the upstream editor notes file, upstream CI that pushes/schedules
# 3) apply-branding.py (every MAE change; stops if an edit no longer matches exactly once) + gen-workflow.py
# 4) bring in the MAE files from the current branch, then sync into rustdesk/ (the git working tree), so that
#    `git -C rustdesk diff` shows exactly the upstream changes. Check: run it with the tag the branch is built on -> no diff.
set -euo pipefail
TAG=${1:?usage: update-upstream.sh <upstream-tag>}
DIR=$(cd "$(dirname "$0")" && pwd)
UP=$DIR/up-$TAG NEW=$DIR/new-$TAG
[ -z "$(git -C "$DIR/rustdesk" status --porcelain --ignored)" ] || { echo "STOP: rustdesk/ has uncommitted or untracked files"; exit 1; }
[ -d "$UP" ] || git clone -q --depth 1 --branch "$TAG" --recurse-submodules --shallow-submodules https://github.com/rustdesk/rustdesk.git "$UP"
rm -rf "$NEW" && mkdir "$NEW"
(cd "$UP" && git ls-files --recurse-submodules -z | tar --null -cf - -T -) | tar -xf - -C "$NEW"
rm -f "$NEW/.gitmodules" "$NEW/CLAUDE.md"
for w in ci clear-cache fdroid flutter-ci flutter-nightly flutter-tag playground update-webpki-roots; do
  rm -f "$NEW/.github/workflows/$w.yml"
done
python3 "$DIR/apply-branding.py" "$NEW" > "$NEW.apply.log" || { tail -3 "$NEW.apply.log"; exit 1; }
python3 "$DIR/gen-workflow.py" "$NEW"
for f in README.md MAE-CHANGES.md CODE_SIGNING_POLICY.md CODE_OF_CONDUCT.md; do cp "$DIR/rustdesk/$f" "$NEW/$f"; done
cp "$DIR/apply-branding.py" "$DIR/gen-workflow.py" "$DIR/update-upstream.sh" "$NEW/"
rsync -a --delete --exclude .git "$NEW/" "$DIR/rustdesk/"
echo "rustdesk/ = upstream $TAG + MAE changes. Review: git -C rustdesk status --short; git -C rustdesk diff --stat"
