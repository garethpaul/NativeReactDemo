#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/native-react-authority-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES ROOT SHELL PYTHON PYTHONPATH

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/native react's [gate] \"quoted\" \`touch NATIVE_REACT_BACKTICK_MARKER\`"
ATTACKER_ROOT="$TEMP_ROOT/attacker-root"
RUN_LOG="$TEMP_ROOT/run.log"
FAKE_SHELL_LOG="$TEMP_ROOT/fake-shell.log"
PATH_SHADOW_LOG="$TEMP_ROOT/path-shadow.log"
mkdir -p "$CONTROL_DIR" "$CHECKOUT/scripts" "$CHECKOUT/tests" "$CHECKOUT/bin" "$ATTACKER_ROOT"
CONTROL_DIR=$(CDPATH='' cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH='' cd -- "$CHECKOUT" && /bin/pwd -P)

cp "$ROOT_DIR/Makefile" "$CHECKOUT/Makefile"
cp "$ROOT_DIR/scripts/run-python.sh" "$CHECKOUT/scripts/run-python.sh"
cat >"$CHECKOUT/scripts/check-baseline.py" <<'PY'
import os
with open(os.environ["NATIVE_REACT_RUN_LOG"], "a", encoding="utf-8") as handle:
    handle.write("static\n")
PY
cat >"$CHECKOUT/tests/test_dummy.py" <<'PY'
import os
import unittest
with open(os.environ["NATIVE_REACT_RUN_LOG"], "a", encoding="utf-8") as handle:
    handle.write("test\n")
class DummyTest(unittest.TestCase):
    def test_true(self):
        self.assertTrue(True)
PY
cat >"$CHECKOUT/scripts/test-makefile-root.sh" <<'SH'
#!/bin/sh
set -eu
printf '%s\n' root >>"$NATIVE_REACT_RUN_LOG"
SH
chmod +x "$CHECKOUT/scripts/run-python.sh" "$CHECKOUT/scripts/test-makefile-root.sh"

cat >"$TEMP_ROOT/fake-shell" <<'SH'
#!/bin/sh
printf '%s\n' "$*" >>"$NATIVE_REACT_FAKE_SHELL_LOG"
exit 0
SH
chmod +x "$TEMP_ROOT/fake-shell"
cat >"$CHECKOUT/bin/python3" <<'SH'
#!/bin/sh
printf '%s\n' "$*" >>"$NATIVE_REACT_PATH_SHADOW_LOG"
exit 0
SH
chmod +x "$CHECKOUT/bin/python3"

run_case() {
    target=$1
    mode=$2
    rm -f "$RUN_LOG" "$FAKE_SHELL_LOG" "$PATH_SHADOW_LOG"
    case $mode in
        default) set -- ;;
        command-root) set -- ROOT="$ATTACKER_ROOT" ;;
        environment-root) set -- ;;
        command-shell) set -- SHELL="$TEMP_ROOT/fake-shell" .SHELLFLAGS=-c ;;
        environment-shell) set -- ;;
        command-python) set -- PYTHON="$CHECKOUT/bin/python3" ;;
        environment-python) set -- ;;
        *) exit 2 ;;
    esac
    if [ "$mode" = environment-root ]; then
        (cd "$CONTROL_DIR" && ROOT="$ATTACKER_ROOT" PATH="$CHECKOUT/bin:/usr/bin:/bin" NATIVE_REACT_RUN_LOG="$RUN_LOG" NATIVE_REACT_FAKE_SHELL_LOG="$FAKE_SHELL_LOG" NATIVE_REACT_PATH_SHADOW_LOG="$PATH_SHADOW_LOG" /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" "$target" "$@") >/dev/null
    elif [ "$mode" = environment-shell ]; then
        (cd "$CONTROL_DIR" && SHELL="$TEMP_ROOT/fake-shell" PATH="$CHECKOUT/bin:/usr/bin:/bin" NATIVE_REACT_RUN_LOG="$RUN_LOG" NATIVE_REACT_FAKE_SHELL_LOG="$FAKE_SHELL_LOG" NATIVE_REACT_PATH_SHADOW_LOG="$PATH_SHADOW_LOG" /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" "$target" "$@") >/dev/null
    elif [ "$mode" = environment-python ]; then
        (cd "$CONTROL_DIR" && PYTHON="$CHECKOUT/bin/python3" PATH="$CHECKOUT/bin:/usr/bin:/bin" NATIVE_REACT_RUN_LOG="$RUN_LOG" NATIVE_REACT_FAKE_SHELL_LOG="$FAKE_SHELL_LOG" NATIVE_REACT_PATH_SHADOW_LOG="$PATH_SHADOW_LOG" /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" "$target" "$@") >/dev/null
    else
        (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:/usr/bin:/bin" NATIVE_REACT_RUN_LOG="$RUN_LOG" NATIVE_REACT_FAKE_SHELL_LOG="$FAKE_SHELL_LOG" NATIVE_REACT_PATH_SHADOW_LOG="$PATH_SHADOW_LOG" /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" "$target" "$@") >/dev/null
    fi
    [ ! -e "$FAKE_SHELL_LOG" ]
    [ ! -e "$PATH_SHADOW_LOG" ]
}

executed=0
for target in build check lint static-check test verify; do
    for mode in default command-root environment-root command-shell environment-shell command-python environment-python; do
        run_case "$target" "$mode"
        executed=$((executed + 1))
    done
done
[ "$executed" -eq 42 ]
[ ! -e "$CONTROL_DIR/NATIVE_REACT_BACKTICK_MARKER" ]

if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/list.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list.out"
if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted /usr/bin/make --environment-overrides --no-print-directory -f "$CHECKOUT/Makefile" check) >"$TEMP_ROOT/list-env.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list-env.out"

PRELOAD="$TEMP_ROOT/preload.mk"
PRELOAD_MARKER="$TEMP_ROOT/preload-ran"
printf '%s\n' "\$(shell /usr/bin/touch '$PRELOAD_MARKER')" >"$PRELOAD"
if (cd "$CONTROL_DIR" && MAKEFILES="$PRELOAD" /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" check) >"$TEMP_ROOT/preload.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/preload.out"
[ -e "$PRELOAD_MARKER" ]

EARLY="$TEMP_ROOT/early.mk"
EARLY_MARKER="$TEMP_ROOT/early-ran"
printf '%s\n' "\$(shell /usr/bin/touch '$EARLY_MARKER')" >"$EARLY"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$EARLY" -f "$CHECKOUT/Makefile" check) >"$TEMP_ROOT/early.out" 2>&1; then exit 1; fi
[ -e "$EARLY_MARKER" ]

LATER="$TEMP_ROOT/later.mk"
LATER_PARSE_MARKER="$TEMP_ROOT/later-parse-ran"
LATER_RECIPE_MARKER="$TEMP_ROOT/later-recipe-ran"
cat >"$LATER" <<EOF
\$(shell /usr/bin/touch '$LATER_PARSE_MARKER')
check:: SHELL := $TEMP_ROOT/fake-shell
check::
	@/usr/bin/touch '$LATER_RECIPE_MARKER'
EOF
if (cd "$CONTROL_DIR" && NATIVE_REACT_FAKE_SHELL_LOG="$FAKE_SHELL_LOG" /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" -f "$LATER" check) >"$TEMP_ROOT/later.out" 2>&1; then exit 1; fi
grep -Fq 'repository Makefile must be loaded alone' "$TEMP_ROOT/later.out"
[ -e "$LATER_PARSE_MARKER" ]
[ ! -e "$LATER_RECIPE_MARKER" ]
[ ! -e "$FAKE_SHELL_LOG" ]

for flag in -n --just-print --dry-run --recon -t --touch -q --question -i --ignore-errors; do
    if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory "$flag" -f "$CHECKOUT/Makefile" check) >"$TEMP_ROOT/mode.out" 2>&1; then exit 1; fi
    grep -Fq 'non-executing or error-ignoring MAKEFLAGS are not supported' "$TEMP_ROOT/mode.out"
done
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$CHECKOUT/Makefile" MAKEFLAGS=-n check) >"$TEMP_ROOT/flags.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFLAGS must not be overridden' "$TEMP_ROOT/flags.out"

printf '%s\n' 'NativeReact Make authority tests passed: 42 target/authority cases, 2 MAKEFILE_LIST rejections, 3 startup/multi-file boundaries, and 11 unsafe mode rejections'
