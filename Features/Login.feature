@smoke @login
Feature: Login

  Scenario: User logs in with valid credentials
    Given user is on login screen
    When user logs in with valid credentials
    Then app home header should be visible
    When user logs out from home menu
    Then user should be on login screen

  Scenario: User sees error for invalid password
    Given user is on login screen
    When user logs in with invalid credentials
    Then invalid credential alert should be visible
    When user dismisses invalid credential alert
    Then user should be on login screen

  @negative
  Scenario: Login page defaults are correct
    Given user is on login screen
    Then email and password placeholders should be visible
    And login button should be disabled

  @negative
  Scenario: Login button stays disabled for missing required fields
    Given user is on login screen
    When user enters email "VALID_EMAIL" and password ""
    Then login button should be disabled
    When user enters email "" and password "VALID_PASSWORD"
    Then login button should be disabled

  @negative
  Scenario Outline: Invalid authentication combinations should fail safely
    Given user is on login screen
    When user enters email "<email_input>" and password "<password_input>"
    And user taps login button
    Then authentication should fail safely

    Examples:
      | email_input                 | password_input |
      | invalid.user@example.com    | WrongPass@123  |
      | VALID_EMAIL                 | WrongPass@123  |
      | unknown.user@shoppix.test   | Test@123       |
      | SPACED_INVALID_EMAIL        | WrongPass@123  |
