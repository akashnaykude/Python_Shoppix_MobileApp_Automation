@welcome
Feature: Welcome screen

  Scenario: Welcome screen loads with expected UI content
    Given user is on welcome screen
    Then welcome screen loads with expected UI content

  Scenario: Existing user can navigate from welcome to login
    Given user is on welcome screen
    When user taps Login as existing User
    Then login screen should be displayed
    When user presses Android back from login screen

  Scenario: Double tap on existing user CTA still opens login
    Given user is on welcome screen
    When user taps Login as existing User twice quickly
    Then login screen should be displayed
    When user presses Android back from login screen

  Scenario: Back from login returns user to welcome
    Given user is on welcome screen
    When user taps Login as existing User
    Then login screen should be displayed
    When user presses Android back from login screen
    Then welcome screen should be displayed again

  Scenario: Facebook registration button is visible on welcome screen
    Given user is on welcome screen
    Then Facebook registration button should be visible

  Scenario: Email registration button is visible on welcome screen
    Given user is on welcome screen
    Then Email registration button should be visible

  Scenario: Welcome screen shows app logo and heading text
    Given user is on welcome screen
    Then app logo should be visible
    And welcome heading should be visible

  Scenario: Welcome screen shows subtitle text
    Given user is on welcome screen
    Then welcome screen subtitle should be visible

  Scenario: Welcome screen shows register with text
    Given user is on welcome screen
    Then register with text should be visible

  Scenario: Footer version text is visible on welcome screen
    Given user is on welcome screen
    Then footer version text should be visible

  Scenario: User can tap Facebook icon from welcome screen
    Given user is on welcome screen
    When user taps Facebook registration icon
    Then Facebook login flow should be displayed

  Scenario: User can tap Email icon from welcome screen
    Given user is on welcome screen
    When user taps Email registration icon
    Then email registration flow should be displayed
    When user cancels email registration

  Scenario: Facebook login flow handles cancel action
    Given user is on welcome screen
    When user taps Facebook registration icon
    And user cancels Facebook login
    Then user should return to welcome screen

  Scenario: Email registration flow handles cancel action
    Given user is on welcome screen
    When user taps Email registration icon
    And user cancels email registration
    Then user should return to welcome screen

  Scenario: Welcome screen remains stable after app background and resume
    Given user is on welcome screen
    When app is sent to background
    And app is brought to foreground
    Then welcome screen should be displayed

  Scenario: Welcome screen is displayed correctly after orientation change
    Given user is on welcome screen
    When device orientation is changed
    Then welcome screen should be displayed correctly

  Scenario: Welcome screen supports back press without crashing
    Given user is on welcome screen
    When user presses Android back
    Then app should handle back press gracefully
