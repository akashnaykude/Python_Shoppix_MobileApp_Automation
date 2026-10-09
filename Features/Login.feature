@login
Feature: Login screen

  Scenario: Login screen loads with expected UI content
    Given user is on login screen
    Then login screen should display expected UI content

  Scenario: Login screen shows app logo
    Given user is on login screen
    Then login app logo should be visible

  Scenario: Login screen shows welcome heading
    Given user is on login screen
    Then login welcome heading should be visible

  Scenario: Login screen shows subtitle text
    Given user is on login screen
    Then login subtitle text should be visible

  Scenario: Login screen shows email field label
    Given user is on login screen
    Then email field label should be visible

  Scenario: Login screen shows email input placeholder
    Given user is on login screen
    Then email input should show placeholder text

  Scenario: Login screen shows password field label
    Given user is on login screen
    Then password field label should be visible

  Scenario: Login screen shows password input placeholder
    Given user is on login screen
    Then password input should show placeholder text

  Scenario: Login screen shows password visibility toggle icon
    Given user is on login screen
    Then password visibility toggle icon should be visible

  Scenario: Login screen shows forgot password link
    Given user is on login screen
    Then forgot password link should be visible

  Scenario: Login screen shows login button
    Given user is on login screen
    Then login button should be visible

  Scenario: Login screen shows social login section text
    Given user is on login screen
    Then social login section text should be visible

  Scenario: Login screen shows Facebook login button
    Given user is on login screen
    Then Facebook login button should be visible

  Scenario: Login screen shows sign up link
    Given user is on login screen
    Then sign up link should be visible

  Scenario: Email field accepts valid email address
    Given user is on login screen
    When user enters valid email address
    Then email input should show entered value

  Scenario: Email field rejects invalid email format
    Given user is on login screen
    When user enters invalid email address
    Then email format validation message should be displayed

  Scenario: Password field accepts valid password
    Given user is on login screen
    When user enters valid password
    Then password input should show masked value

  Scenario: Password field is masked by default
    Given user is on login screen
    Then password should be hidden by default

  Scenario: User can toggle password visibility on
    Given user is on login screen
    When user enters dummy password for visibility check
    When user taps password visibility toggle icon
    Then password should be visible

  Scenario: User can toggle password visibility off
    Given user is on login screen
    When user enters dummy password for visibility check
    When user taps password visibility toggle icon
    And user taps password visibility toggle icon again
    Then password should be hidden

  Scenario: Login button remains disabled when email is empty
    Given user is on login screen
    When user leaves email field empty
    And user enters valid password
    Then login button should be disabled

  Scenario: Login button remains disabled when password is empty
    Given user is on login screen
    When user enters valid email address
    And user leaves password field empty
    Then login button should be disabled

  Scenario: Login button remains disabled when both fields are empty
    Given user is on login screen
    Then login button should be disabled

  Scenario: Login button becomes enabled when valid email and password are entered
    Given user is on login screen
    When user enters valid email address
    And user enters valid password
    Then login button should be enabled

  @smoke
  Scenario: User can login with valid credentials
    Given user is on login screen
    When user enters valid email address
    And user enters valid password
    And user taps login button
    Then user should be logged in successfully
    When user logs out from home menu
    Then user should be on login screen

  Scenario: Login fails with incorrect password
    Given user is on login screen
    When user enters valid email address
    And user enters invalid password
    And user taps login button
    Then invalid credentials message should be displayed

  Scenario: Login fails with unregistered email
    Given user is on login screen
    When user enters unregistered email address
    And user enters valid password
    And user taps login button
    Then invalid credentials message should be displayed

  Scenario: Login fails when email format is invalid and password is entered
    Given user is on login screen
    When user enters invalid email address
    And user enters valid password
    And user taps login button
    Then email format validation message should be displayed

  Scenario: Login fails when email field is empty and password is entered
    Given user is on login screen
    When user leaves email field empty
    And user enters valid password
    And user taps login button
    Then email required validation message should be displayed

  Scenario: Login fails when password field is empty and email is entered
    Given user is on login screen
    When user enters valid email address
    And user leaves password field empty
    And user taps login button
    Then password required validation message should be displayed

  Scenario: Forgot password link opens forgot password screen
    Given user is on login screen
    When user taps forgot password link
    Then forgot password screen should be displayed
    When user presses Android back
    Then login screen should be displayed

  Scenario: Facebook login button opens Facebook auth flow
    Given user is on login screen
    When user taps Facebook login button
    Then Facebook auth flow should be displayed

  Scenario: Facebook login cancel returns user to login screen
    Given user is on login screen
    When user taps Facebook login button
    And user cancels Facebook login
    Then login screen should be displayed

  Scenario: Sign up link opens registration screen
    Given user is on login screen
    When user taps sign up link
    Then sign up screen should be displayed
    When user presses Android back
    Then login screen should be displayed quickly

  Scenario: Login screen remains stable after app background and resume
    Given user is on login screen
    When app is sent to background
    And app is brought to foreground
    Then login screen should be displayed

  Scenario: Login screen remains stable after orientation change
    Given user is on login screen
    When device orientation is changed
    Then login screen should be displayed correctly

  Scenario: Login screen back press behavior is handled correctly
    Given user is on login screen
    When user presses Android back
    Then user should be navigated as per expected back behavior

  Scenario: Login screen elements are accessible
    Given user is on login screen
    Then all visible elements should have accessibility labels
