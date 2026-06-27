# Lexical Module Registration

status: completed

## Problem

The release guard searched raw bundle text for the exact
`AppRegistry.registerComponent` prefix and module argument. Comments, strings,
and regular-expression literals could therefore impersonate a registration
even though React Native would never execute that text as a call.

## Options

1. Keep substring matching and add more delimiters. Rejected because literals
   can still contain any delimiter sequence.
2. Add a small lexical scanner. Chosen because it distinguishes code from
   comments, strings, and context-appropriate regular-expression literals while
   preserving the historical Objective-C runtime.
3. Embed a JavaScript parser. Rejected as disproportionate for a legacy sample
   and incompatible with the dependency-preservation boundary.

## Decision

Scan bounded UTF-8 bundle contents as JavaScript lexical states. Skip line and
block comments; single-, double-, and template-quoted strings; and bounded
regular-expression bodies when the preceding token permits an expression.
Preserve ordinary division operators and restricted-statement line terminators,
including U+2028/U+2029 and optional `break` and `continue` labels. In code,
require the global
`AppRegistry` identifier, dot member access,
`registerComponent`, an opening parenthesis, the exact quoted module name, and
the following comma. Allow whitespace and comments between code tokens.

## Verification

Native XCTest rejects registration text inside comments, strings, a regular
expression, control-condition regex statements, semicolon-less restricted
statements, labels, multiline label comments, and a comment-separated member
object while accepting real calls after ordinary and ambiguous division.
Portable tests reject restoration of raw substring matching and removal of the
global-object, regular-expression, restricted-statement, or division-context
boundaries. Canonical root and external-directory `make check` each passed 42
Make authority cases and 26 Python tests. `npm run check`, JavaScript fixture
parsing, `git diff --check`, and current-tree gitleaks passed. Hosted macOS
parses the Xcode project, but the maintained baseline does not compile the
Objective-C target or execute native XCTest; adding a synthetic-header compile
would not represent the legacy project's real dependency graph, and a full
React Native 0.4.2 build is not reproducible in this correction scope.
