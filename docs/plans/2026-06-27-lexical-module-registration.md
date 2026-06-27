# Lexical Module Registration

status: completed

## Problem

The release guard searched raw bundle text for the exact
`AppRegistry.registerComponent` prefix and module argument. Comments and string
literals could therefore impersonate a registration even though React Native
would never execute that text as a call.

## Options

1. Keep substring matching and add more delimiters. Rejected because literals
   can still contain any delimiter sequence.
2. Add a small lexical scanner. Chosen because it distinguishes code from
   comments and strings while preserving the historical Objective-C runtime.
3. Embed a JavaScript parser. Rejected as disproportionate for a legacy sample
   and incompatible with the dependency-preservation boundary.

## Decision

Scan bounded UTF-8 bundle contents as JavaScript lexical states. Skip line and
block comments plus single-, double-, and template-quoted strings. In code,
require the global `AppRegistry` identifier, dot member access,
`registerComponent`, an opening parenthesis, the exact quoted module name, and
the following comma. Allow whitespace and comments between code tokens.

## Verification

Native XCTest rejects registration text inside comments, strings, and a
comment-separated member object while accepting a real trivia-separated call.
Portable tests reject restoration of raw substring matching and removal of the
global-object boundary. Canonical root and external-directory `make check`
remain required before merge.
