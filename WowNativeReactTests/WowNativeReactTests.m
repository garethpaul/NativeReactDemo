/**
 * Copyright (c) 2015-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#import <UIKit/UIKit.h>
#import <XCTest/XCTest.h>

#import "../iOS/AppDelegate.h"
#import "RCTAssert.h"
#import "RCTRedBox.h"
#import "RCTRootView.h"

#define TIMEOUT_SECONDS 240
#define TEXT_TO_LOOK_FOR @"Hi"

@interface AppDelegate (ReleaseBundleValidationTesting)

- (BOOL)bundleContentsMatchReleasePlaceholder:(NSString *)bundleContents;
- (BOOL)bundleContents:(NSString *)bundleContents registersModule:(NSString *)moduleName;
- (BOOL)isPlaceholderBundleAtURL:(NSURL *)bundleURL;

@end

@interface WowNativeReactTests : XCTestCase

@end

@implementation WowNativeReactTests

- (NSURL *)temporaryBundleURLWithContents:(NSString *)contents
{
  NSString *fileName = [NSString stringWithFormat:@"%@.jsbundle", [[NSUUID UUID] UUIDString]];
  NSURL *bundleURL = [NSURL fileURLWithPath:[NSTemporaryDirectory() stringByAppendingPathComponent:fileName]];
  NSError *error = nil;
  BOOL wroteBundle = [contents writeToURL:bundleURL
                               atomically:YES
                                 encoding:NSUTF8StringEncoding
                                    error:&error];
  XCTAssertTrue(wroteBundle, @"Could not write temporary bundle: %@", error);
  return bundleURL;
}

- (void)removeTemporaryBundleAtURL:(NSURL *)bundleURL
{
  NSError *error = nil;
  BOOL removedBundle = [[NSFileManager defaultManager] removeItemAtURL:bundleURL error:&error];
  XCTAssertTrue(removedBundle, @"Could not remove temporary bundle: %@", error);
}

- (void)testRejectsCheckedInReleasePlaceholder
{
  NSString *placeholder = @"// Offline JS\n"
      @"// To re-generate the offline bundle, run this from the root of your project:\n\n"
      @"// $ react-native bundle --minify\n"
      @"//\n"
      @"// See http://facebook.github.io/react-native/docs/runningondevice.html for more details.\n\n"
      @"throw new Error('Offline JS file is empty. See iOS/main.jsbundle for instructions');\n";
  NSURL *bundleURL = [self temporaryBundleURLWithContents:placeholder];
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertTrue([delegate bundleContentsMatchReleasePlaceholder:placeholder]);
  XCTAssertTrue([delegate isPlaceholderBundleAtURL:bundleURL]);

  [self removeTemporaryBundleAtURL:bundleURL];
}

- (void)testAcceptsRegisteredBundleContainingPlaceholderMarker
{
  NSString *bundleContents = @"AppRegistry.registerComponent('WowNativeReact', function() { return null; });\n"
      @"var diagnostic = 'Offline JS file is empty';\n";
  NSURL *bundleURL = [self temporaryBundleURLWithContents:bundleContents];
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertFalse([delegate bundleContentsMatchReleasePlaceholder:bundleContents]);
  XCTAssertFalse([delegate isPlaceholderBundleAtURL:bundleURL]);

  [self removeTemporaryBundleAtURL:bundleURL];
}

- (void)testAcceptsRegisteredBundleWithPlaceholderBoundariesAndAdditionalContent
{
  NSString *bundleContents = @"// Offline JS\n"
      @"AppRegistry.registerComponent('WowNativeReact', function() { return null; });\n"
      @"throw new Error('Offline JS file is empty. See iOS/main.jsbundle for instructions');\n";
  NSURL *bundleURL = [self temporaryBundleURLWithContents:bundleContents];
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertFalse([delegate bundleContentsMatchReleasePlaceholder:bundleContents]);
  XCTAssertFalse([delegate isPlaceholderBundleAtURL:bundleURL]);

  [self removeTemporaryBundleAtURL:bundleURL];
}

- (void)testRejectsPrefixModuleRegistration
{
  NSString *bundleContents = @"AppRegistry.registerComponent('WowNativeReactPreview', function() { return null; });\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertFalse([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
}

- (void)testRejectsRegistrationTextInsideCommentsAndStrings
{
  NSArray *bundleContentsCases = @[
    @"// AppRegistry.registerComponent('WowNativeReact', function() {});\n",
    @"/* AppRegistry.registerComponent(\"WowNativeReact\", function() {}); */\n",
    @"var diagnostic = \"AppRegistry.registerComponent('WowNativeReact',\";\n",
    @"var bridge = {}; bridge. /* trivia */ AppRegistry.registerComponent('WowNativeReact', function() {});\n",
  ];
  AppDelegate *delegate = [[AppDelegate alloc] init];

  for (NSString *bundleContents in bundleContentsCases) {
    NSURL *bundleURL = [self temporaryBundleURLWithContents:bundleContents];
    XCTAssertFalse([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
    XCTAssertTrue([delegate isPlaceholderBundleAtURL:bundleURL]);
    [self removeTemporaryBundleAtURL:bundleURL];
  }
}

- (void)testAcceptsLexicalRegistrationWithWhitespace
{
  NSString *bundleContents = @"AppRegistry /* bridge */ . registerComponent ( \"WowNativeReact\" , function() {});\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertTrue([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
}

- (void)testRejectsRegistrationTextInsideRegularExpression
{
  NSString *bundleContents = @"var diagnostic = /AppRegistry.registerComponent('WowNativeReact',.*)/;\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];
  NSURL *bundleURL = [self temporaryBundleURLWithContents:bundleContents];

  XCTAssertFalse([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
  XCTAssertTrue([delegate isPlaceholderBundleAtURL:bundleURL]);
  [self removeTemporaryBundleAtURL:bundleURL];
}

- (void)testAcceptsRegistrationAfterDivisionExpression
{
  NSString *bundleContents = @"var ratio = total / count;\nAppRegistry.registerComponent('WowNativeReact', function() {});\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertTrue([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
}

- (void)testRejectsRegularExpressionAfterControlCondition
{
  NSString *bundleContents = @"if (ready) /AppRegistry.registerComponent('WowNativeReact',.*)/.test(source);\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertFalse([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
}

- (void)testRejectsRegularExpressionAfterRestrictedStatement
{
  NSArray *bundleContentsCases = @[
    @"while (ready) { break\n/AppRegistry.registerComponent('WowNativeReact',.*)/.test(source); }\n",
    @"outer: while (ready) { continue outer\n/AppRegistry.registerComponent('WowNativeReact',.*)/.test(source); }\n",
    @"outer: while (ready) { break outer /* label comment\n*/ /AppRegistry.registerComponent('WowNativeReact',.*)/.test(source); }\n",
    @"debugger\n/AppRegistry.registerComponent('WowNativeReact',.*)/.test(source);\n",
    @"outer: while (ready) { continue outer\u2028/AppRegistry.registerComponent('WowNativeReact',.*)/.test(source); }\n",
    @"outer: while (ready) { break outer\u2029/AppRegistry.registerComponent('WowNativeReact',.*)/.test(source); }\n",
  ];
  AppDelegate *delegate = [[AppDelegate alloc] init];

  for (NSString *bundleContents in bundleContentsCases) {
    XCTAssertFalse([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
  }
}

- (void)testAcceptsRegistrationAfterPostfixDivisionExpression
{
  NSString *bundleContents = @"var ratio = total++ / count;\nAppRegistry.registerComponent('WowNativeReact', function() {});\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertTrue([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
}

- (void)testAcceptsRegistrationAfterAmbiguousDivisionExpression
{
  NSString *bundleContents = @"var ratio = {} / count;\nAppRegistry.registerComponent('WowNativeReact', function() {});\n";
  AppDelegate *delegate = [[AppDelegate alloc] init];

  XCTAssertTrue([delegate bundleContents:bundleContents registersModule:@"WowNativeReact"]);
}

- (BOOL)findSubviewInView:(UIView *)view matching:(BOOL(^)(UIView *view))test
{
  if (test(view)) {
    return YES;
  }
  for (UIView *subview in [view subviews]) {
    if ([self findSubviewInView:subview matching:test]) {
      return YES;
    }
  }
  return NO;
}

- (NSString *)textForView:(UIView *)view
{
  if ([view respondsToSelector:@selector(attributedText)]) {
    NSAttributedString *attributedText = [(id)view attributedText];
    if (attributedText.string.length > 0) {
      return attributedText.string;
    }
  }

  if ([view respondsToSelector:@selector(text)]) {
    NSString *text = [(id)view text];
    if (text.length > 0) {
      return text;
    }
  }

  return nil;
}

- (void)testRendersWelcomeScreen {
  UIViewController *vc = [[[[UIApplication sharedApplication] delegate] window] rootViewController];
  NSDate *date = [NSDate dateWithTimeIntervalSinceNow:TIMEOUT_SECONDS];
  BOOL foundElement = NO;
  NSString *redboxError = nil;

  while ([date timeIntervalSinceNow] > 0 && !foundElement && !redboxError) {
    [[NSRunLoop mainRunLoop] runMode:NSDefaultRunLoopMode beforeDate:[NSDate dateWithTimeIntervalSinceNow:0.1]];
    [[NSRunLoop mainRunLoop] runMode:NSRunLoopCommonModes beforeDate:[NSDate dateWithTimeIntervalSinceNow:0.1]];

    redboxError = [[RCTRedBox sharedInstance] currentErrorMessage];

    foundElement = [self findSubviewInView:vc.view matching:^BOOL(UIView *view) {
      NSString *text = [self textForView:view];
      return [text isEqualToString:TEXT_TO_LOOK_FOR];
    }];
  }

  XCTAssertNil(redboxError, @"RedBox error: %@", redboxError);
  XCTAssertTrue(foundElement, @"Couldn't find element with text '%@' in %d seconds", TEXT_TO_LOOK_FOR, TIMEOUT_SECONDS);
}


@end
