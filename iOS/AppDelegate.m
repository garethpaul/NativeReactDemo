/**
 * Copyright (c) 2015-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#import "AppDelegate.h"

#import "RCTRootView.h"

static NSString * const NativeReactModuleName = @"WowNativeReact";
static NSString * const ReleasePlaceholderContents =
    @"// Offline JS\n"
    @"// To re-generate the offline bundle, run this from the root of your project:\n"
    @"//\n"
    @"// $ react-native bundle --minify\n"
    @"//\n"
    @"// See http://facebook.github.io/react-native/docs/runningondevice.html for more details.\n"
    @"\n"
    @"throw new Error('Offline JS file is empty. See iOS/main.jsbundle for instructions');";
static const unsigned long long MaximumReleaseBundleBytes = 10ULL * 1024ULL * 1024ULL;

@implementation AppDelegate

- (BOOL)isJavaScriptIdentifierCharacter:(unichar)character
{
  return (character >= 'a' && character <= 'z') ||
      (character >= 'A' && character <= 'Z') ||
      (character >= '0' && character <= '9') ||
      character == '_' || character == '$';
}

- (BOOL)skipJavaScriptStringOrCommentInContents:(NSString *)contents index:(NSUInteger *)index
{
  NSUInteger length = contents.length;
  if (*index >= length) {
    return NO;
  }

  unichar first = [contents characterAtIndex:*index];
  if (first == '\'' || first == '"' || first == '`') {
    unichar quote = first;
    *index += 1;
    while (*index < length) {
      unichar character = [contents characterAtIndex:*index];
      *index += 1;
      if (character == '\\' && *index < length) {
        *index += 1;
      } else if (character == quote) {
        break;
      }
    }
    return YES;
  }

  if (first != '/' || *index + 1 >= length) {
    return NO;
  }

  unichar second = [contents characterAtIndex:*index + 1];
  if (second == '/') {
    *index += 2;
    while (*index < length) {
      unichar character = [contents characterAtIndex:*index];
      *index += 1;
      if (character == '\n' || character == '\r') {
        break;
      }
    }
    return YES;
  }
  if (second == '*') {
    *index += 2;
    while (*index + 1 < length) {
      if ([contents characterAtIndex:*index] == '*' &&
          [contents characterAtIndex:*index + 1] == '/') {
        *index += 2;
        return YES;
      }
      *index += 1;
    }
    *index = length;
    return YES;
  }
  return NO;
}

- (void)skipJavaScriptTriviaInContents:(NSString *)contents index:(NSUInteger *)index
{
  NSCharacterSet *whitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
  while (*index < contents.length) {
    unichar character = [contents characterAtIndex:*index];
    if ([whitespace characterIsMember:character]) {
      *index += 1;
      continue;
    }
    if (character == '/' && *index + 1 < contents.length) {
      unichar next = [contents characterAtIndex:*index + 1];
      if (next == '/' || next == '*') {
        [self skipJavaScriptStringOrCommentInContents:contents index:index];
        continue;
      }
    }
    break;
  }
}

- (BOOL)skipJavaScriptRegularExpressionInContents:(NSString *)contents index:(NSUInteger *)index
{
  NSUInteger length = contents.length;
  if (*index >= length || [contents characterAtIndex:*index] != '/') {
    return NO;
  }

  NSUInteger regularExpressionStart = *index;
  *index += 1;
  BOOL insideCharacterClass = NO;
  while (*index < length) {
    unichar character = [contents characterAtIndex:*index];
    *index += 1;
    if (character == '\n' || character == '\r') {
      *index = regularExpressionStart;
      return NO;
    }
    if (character == '\\' && *index < length) {
      *index += 1;
      continue;
    }
    if (character == '[') {
      insideCharacterClass = YES;
      continue;
    }
    if (character == ']' && insideCharacterClass) {
      insideCharacterClass = NO;
      continue;
    }
    if (character == '/' && !insideCharacterClass) {
      while (*index < length &&
             [self isJavaScriptIdentifierCharacter:[contents characterAtIndex:*index]]) {
        *index += 1;
      }
      return YES;
    }
  }
  *index = regularExpressionStart;
  return NO;
}

- (BOOL)identifierAtIndex:(NSUInteger *)index
               inContents:(NSString *)contents
                   matches:(NSString *)identifier
{
  NSUInteger start = *index;
  NSUInteger end = start + identifier.length;
  if (end > contents.length ||
      ![[contents substringWithRange:NSMakeRange(start, identifier.length)] isEqualToString:identifier]) {
    return NO;
  }
  if (start > 0) {
    unichar previous = [contents characterAtIndex:start - 1];
    if ([self isJavaScriptIdentifierCharacter:previous]) {
      return NO;
    }
  }
  if (end < contents.length && [self isJavaScriptIdentifierCharacter:[contents characterAtIndex:end]]) {
    return NO;
  }
  *index = end;
  return YES;
}

- (BOOL)bundleContents:(NSString *)bundleContents registersModule:(NSString *)moduleName
{
  if (bundleContents == nil || moduleName == nil) {
    return NO;
  }

  NSString *trimmedModuleName = [moduleName stringByTrimmingCharactersInSet:
                                 [NSCharacterSet whitespaceAndNewlineCharacterSet]];
  if (trimmedModuleName.length == 0) {
    return NO;
  }

  // Scan JavaScript tokens so registration text inside comments and strings cannot pass.
  // Reject registration text inside regular expressions as non-code.
  NSUInteger index = 0;
  BOOL previousTokenWasDot = NO;
  BOOL canStartRegularExpression = YES;
  BOOL nextParenthesisStartsControlHeader = NO;
  NSCharacterSet *javascriptWhitespace = [NSCharacterSet whitespaceAndNewlineCharacterSet];
  NSMutableArray *parenthesisContexts = [NSMutableArray array];
  NSSet *regularExpressionPrefixKeywords = [NSSet setWithObjects:
      @"await", @"case", @"delete", @"do", @"else", @"in", @"instanceof", @"new",
      @"of", @"return", @"throw", @"typeof", @"void", @"yield", nil];
  NSSet *regularExpressionControlKeywords = [NSSet setWithObjects:
      @"catch", @"for", @"if", @"switch", @"while", @"with", nil];
  while (index < bundleContents.length) {
    unichar currentCharacter = [bundleContents characterAtIndex:index];
    if ([javascriptWhitespace characterIsMember:currentCharacter]) {
      index += 1;
      continue;
    }
    BOOL currentTokenIsString = currentCharacter == '\'' || currentCharacter == '"' || currentCharacter == '`';
    if ([self skipJavaScriptStringOrCommentInContents:bundleContents index:&index]) {
      if (currentTokenIsString) {
        previousTokenWasDot = NO;
        canStartRegularExpression = NO;
        nextParenthesisStartsControlHeader = NO;
      }
      continue;
    }
    if (currentCharacter == '/' && canStartRegularExpression &&
        [self skipJavaScriptRegularExpressionInContents:bundleContents index:&index]) {
      previousTokenWasDot = NO;
      canStartRegularExpression = NO;
      nextParenthesisStartsControlHeader = NO;
      continue;
    }

    NSUInteger candidate = index;
    if (previousTokenWasDot) {
      previousTokenWasDot = NO;
      canStartRegularExpression = NO;
      nextParenthesisStartsControlHeader = NO;
      index += 1;
      continue;
    }
    if (![self identifierAtIndex:&candidate inContents:bundleContents matches:@"AppRegistry"]) {
      if ([self isJavaScriptIdentifierCharacter:currentCharacter]) {
        NSUInteger identifierStart = index;
        while (index < bundleContents.length &&
               [self isJavaScriptIdentifierCharacter:[bundleContents characterAtIndex:index]]) {
          index += 1;
        }
        NSString *identifier = [bundleContents substringWithRange:
                                NSMakeRange(identifierStart, index - identifierStart)];
        canStartRegularExpression = [regularExpressionPrefixKeywords containsObject:identifier];
        nextParenthesisStartsControlHeader = [regularExpressionControlKeywords containsObject:identifier];
        previousTokenWasDot = NO;
        continue;
      }
      if (currentCharacter == '(') {
        [parenthesisContexts addObject:[NSNumber numberWithBool:nextParenthesisStartsControlHeader]];
        canStartRegularExpression = YES;
        previousTokenWasDot = NO;
        nextParenthesisStartsControlHeader = NO;
        index += 1;
        continue;
      }
      if (currentCharacter == ')') {
        BOOL closesControlHeader = NO;
        if (parenthesisContexts.count > 0) {
          closesControlHeader = [[parenthesisContexts lastObject] boolValue];
          [parenthesisContexts removeLastObject];
        }
        canStartRegularExpression = closesControlHeader;
        previousTokenWasDot = NO;
        nextParenthesisStartsControlHeader = NO;
        index += 1;
        continue;
      }
      if ((currentCharacter == '+' || currentCharacter == '-') &&
          index + 1 < bundleContents.length &&
          [bundleContents characterAtIndex:index + 1] == currentCharacter) {
        canStartRegularExpression = NO;
        previousTokenWasDot = NO;
        nextParenthesisStartsControlHeader = NO;
        index += 2;
        continue;
      }
      previousTokenWasDot = currentCharacter == '.';
      canStartRegularExpression = currentCharacter != ')' && currentCharacter != ']' &&
          currentCharacter != '.';
      nextParenthesisStartsControlHeader = NO;
      index += 1;
      continue;
    }
    previousTokenWasDot = NO;
    nextParenthesisStartsControlHeader = NO;
    [self skipJavaScriptTriviaInContents:bundleContents index:&candidate];
    if (candidate >= bundleContents.length || [bundleContents characterAtIndex:candidate] != '.') {
      index += 1;
      continue;
    }
    candidate += 1;
    [self skipJavaScriptTriviaInContents:bundleContents index:&candidate];
    if (![self identifierAtIndex:&candidate inContents:bundleContents matches:@"registerComponent"]) {
      index += 1;
      continue;
    }
    [self skipJavaScriptTriviaInContents:bundleContents index:&candidate];
    if (candidate >= bundleContents.length || [bundleContents characterAtIndex:candidate] != '(') {
      index += 1;
      continue;
    }
    candidate += 1;
    [self skipJavaScriptTriviaInContents:bundleContents index:&candidate];
    if (candidate >= bundleContents.length) {
      return NO;
    }
    unichar quote = [bundleContents characterAtIndex:candidate];
    if (quote != '\'' && quote != '"') {
      index += 1;
      continue;
    }
    candidate += 1;
    if (candidate + trimmedModuleName.length >= bundleContents.length ||
        ![[bundleContents substringWithRange:NSMakeRange(candidate, trimmedModuleName.length)]
            isEqualToString:trimmedModuleName]) {
      index += 1;
      continue;
    }
    candidate += trimmedModuleName.length;
    if ([bundleContents characterAtIndex:candidate] != quote) {
      index += 1;
      continue;
    }
    candidate += 1;
    [self skipJavaScriptTriviaInContents:bundleContents index:&candidate];
    if (candidate < bundleContents.length && [bundleContents characterAtIndex:candidate] == ',') {
      return YES;
    }
    index += 1;
  }
  return NO;
}

- (BOOL)bundleContentsMatchReleasePlaceholder:(NSString *)bundleContents
{
  if (bundleContents == nil) {
    return NO;
  }

  NSString *trimmedBundleContents = [bundleContents stringByTrimmingCharactersInSet:
                                     [NSCharacterSet whitespaceAndNewlineCharacterSet]];
  NSString *normalizedBundleContents = [trimmedBundleContents
      stringByReplacingOccurrencesOfString:@"\r\n" withString:@"\n"];
  normalizedBundleContents = [normalizedBundleContents
      stringByReplacingOccurrencesOfString:@"\r" withString:@"\n"];
  return [normalizedBundleContents isEqualToString:ReleasePlaceholderContents];
}

- (BOOL)isPlaceholderBundleAtURL:(NSURL *)bundleURL
{
  if (bundleURL == nil) {
    return YES;
  }
  if (![bundleURL isFileURL]) {
    return YES;
  }

  NSError *error = nil;
  NSDictionary *bundleAttributes = [[NSFileManager defaultManager]
                                    attributesOfItemAtPath:[bundleURL path]
                                    error:&error];
  NSString *bundleType = [bundleAttributes objectForKey:NSFileType];
  NSNumber *bundleSize = [bundleAttributes objectForKey:NSFileSize];
  if (bundleAttributes == nil || bundleType == nil || bundleSize == nil ||
      ![bundleType isEqualToString:NSFileTypeRegular] ||
      [bundleSize unsignedLongLongValue] > MaximumReleaseBundleBytes) {
    return YES;
  }

  error = nil;
  NSString *bundleContents = [NSString stringWithContentsOfURL:bundleURL
                                                      encoding:NSUTF8StringEncoding
                                                         error:&error];
  if (bundleContents == nil) {
    return YES;
  }

  NSString *trimmedBundleContents = [bundleContents stringByTrimmingCharactersInSet:
                                     [NSCharacterSet whitespaceAndNewlineCharacterSet]];
  if (trimmedBundleContents.length == 0) {
    return YES;
  }

  if (![self bundleContents:bundleContents registersModule:NativeReactModuleName]) {
    return YES;
  }

  return [self bundleContentsMatchReleasePlaceholder:bundleContents];
}

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
  
  NSURL *jsCodeLocation;

  /**
   * Loading JavaScript code - uncomment the one you want.
   *
   * OPTION 1
   * Load from development server. Start the server from the repository root:
   *
   * $ npm start
   *
   * To run on device, change `localhost` to the IP address of your computer
   * (you can get this by typing `ifconfig` into the terminal and selecting the
   * `inet` value under `en0:`) and make sure your computer and iOS device are
   * on the same Wi-Fi network.
   */

#if DEBUG
  jsCodeLocation = [NSURL URLWithString:@"http://localhost:8081/index.ios.bundle"];
#else
  jsCodeLocation = [[NSBundle mainBundle] URLForResource:@"main" withExtension:@"jsbundle"];
#endif

  if (jsCodeLocation == nil) {
    return NO;
  }

#ifndef DEBUG
  if ([self isPlaceholderBundleAtURL:jsCodeLocation]) {
    return NO;
  }
#endif

  /**
   * OPTION 2
   * Load from pre-bundled file on disk. To re-generate the static bundle
   * from the root of your project directory, run
   *
   * $ react-native bundle --minify
   *
   * see http://facebook.github.io/react-native/docs/runningondevice.html
   */

  RCTRootView *rootView = [[RCTRootView alloc] initWithBundleURL:jsCodeLocation
                                                      moduleName:NativeReactModuleName
                                                   launchOptions:launchOptions];

  self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];
  UIViewController *rootViewController = [[UIViewController alloc] init];
  rootViewController.view = rootView;
  self.window.rootViewController = rootViewController;
  [self.window makeKeyAndVisible];
  return YES;
}

@end
