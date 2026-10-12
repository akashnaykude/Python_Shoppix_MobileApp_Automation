@waitlist_registration
Feature: Registration flow with waiting list enabled

  # ---- Visibility ------------------------------------------------------
  Scenario: Waiting list registration screen loads successfully
    Given user is on waiting list registration screen
    Then waiting list registration screen should load successfully

  Scenario: App logo is visible on waiting list registration screen
    Given user is on waiting list registration screen
    Then app logo should be visible

  Scenario: Back button is visible on waiting list registration screen
    Given user is on waiting list registration screen
    Then back button should be visible

  Scenario: Main heading is visible on waiting list registration screen
    Given user is on waiting list registration screen
    Then main heading should be visible

  Scenario: Waiting list description text is visible
    Given user is on waiting list registration screen
    Then waiting list description text should be visible

  Scenario: Referral code instruction text is visible
    Given user is on waiting list registration screen
    Then referral code instruction text should be visible

  Scenario: Email field label is visible
    Given user is on waiting list registration screen
    Then email field label should be visible

  Scenario: Email input placeholder is visible
    Given user is on waiting list registration screen
    Then email input placeholder should be visible

  Scenario: Postcode field label is visible
    Given user is on waiting list registration screen
    Then postcode field label should be visible

  Scenario: Postcode input placeholder is visible
    Given user is on waiting list registration screen
    Then postcode input placeholder should be visible

  Scenario: Age range field label is visible
    Given user is on waiting list registration screen
    Then age range field label should be visible

  Scenario: Age range dropdown is visible
    Given user is on waiting list registration screen
    Then age range dropdown should be visible

  Scenario: Referral code label is visible
    Given user is on waiting list registration screen
    Then referral code label should be visible

  Scenario: Referral code input placeholder is visible
    Given user is on waiting list registration screen
    Then referral code input placeholder should be visible

  Scenario: Consent checkbox is visible
    Given user is on waiting list registration screen
    Then consent checkbox should be visible

  Scenario: Consent text is visible
    Given user is on waiting list registration screen
    Then consent text should be visible

  Scenario: Privacy information text is visible
    Given user is on waiting list registration screen
    Then privacy information text should be visible

  Scenario: Continue button is visible
    Given user is on waiting list registration screen
    Then continue button should be visible

  # ---- Email -----------------------------------------------------------
  Scenario: User can enter valid email
    Given user is on waiting list registration screen
    When user enters valid email address
    Then email input should show entered value

  Scenario: Email field shows required validation when empty
    Given user is on waiting list registration screen
    When user leaves email field empty and tries to continue
    Then email required validation message should be displayed

  Scenario: Email field shows invalid format validation
    Given user is on waiting list registration screen
    When user enters invalid email address
    And user tries to continue
    Then email format validation message should be displayed

  Scenario: Email field trims leading and trailing spaces
    Given user is on waiting list registration screen
    When user enters email address with leading and trailing spaces
    Then email input should trim spaces correctly

  # ---- Postcode (UK only) ---------------------------------------------
  Scenario: User can enter postcode
    Given user is on waiting list registration screen
    When user enters postcode
    Then postcode input should show entered value

  Scenario: Postcode field shows required validation when empty
    Given user is on waiting list registration screen
    When user leaves postcode field empty and tries to continue
    Then postcode required validation message should be displayed

  Scenario: Postcode field accepts valid UK postcode format
    Given user is on waiting list registration screen
    When user enters valid UK postcode
    Then postcode should be accepted without validation error

  Scenario: Postcode field rejects non UK postcode format
    Given user is on waiting list registration screen
    When user enters non UK postcode
    And user tries to continue
    Then valid postcode validation message should be displayed

  Scenario: Postcode field rejects invalid UK postcode format
    Given user is on waiting list registration screen
    When user enters invalid UK postcode
    And user tries to continue
    Then valid postcode validation message should be displayed

  Scenario: Postcode field trims spaces
    Given user is on waiting list registration screen
    When user enters postcode with leading and trailing spaces
    Then postcode input should trim spaces correctly

  # ---- Age range -------------------------------------------------------
  Scenario: Age range dropdown opens and shows all expected options
    Given user is on waiting list registration screen
    When user taps age range dropdown
    Then age range options should be displayed
    And all age range options should be visible

  Scenario: Age range field shows required validation when not selected
    Given user is on waiting list registration screen
    When user leaves age range unselected and tries to continue
    Then age range required validation message should be displayed

  Scenario Outline: Age range option is selectable
    Given user is on waiting list registration screen
    When user taps age range dropdown
    And user selects "<age>" age range
    Then selected age range should be "<age>"

    Examples:
      | age   |
      | 18-24 |
      | 25-34 |
      | 35-44 |
      | 45-54 |
      | 55-64 |
      | 65+   |

  # ---- Referral code (UI / input only) --------------------------------
  Scenario: Referral code field accepts typed input
    Given user is on waiting list registration screen
    When user enters referral code
    Then referral code input should show entered value

  Scenario: Referral code field can be left empty
    Given user is on waiting list registration screen
    When user leaves referral code empty
    Then referral code field should remain optional

  # ---- Consent ---------------------------------------------------------
  Scenario: Consent checkbox can be selected
    Given user is on waiting list registration screen
    When user taps consent checkbox
    Then consent checkbox should be selected

  Scenario: Consent checkbox can be deselected
    Given user is on waiting list registration screen
    When user taps consent checkbox
    And user taps consent checkbox again
    Then consent checkbox should be deselected

  # ---- Submit-time validation -----------------------------------------
  # Grounded in page_source: Continue stays enabled and validates on tap.
  Scenario: Continue with empty required fields shows validation errors
    Given user is on waiting list registration screen
    When user taps continue button
    Then required field validation messages should be displayed

  Scenario: Continue without consent shows consent validation
    Given user is on waiting list registration screen
    When user enters valid email address
    And user enters valid UK postcode
    And user selects an age range option
    And user taps continue button
    Then consent validation message should be displayed

  # ---- Success (single compact scenario) ------------------------------
  Scenario: User can submit valid waiting list registration successfully
    Given user is on waiting list registration screen
    When user enters valid email address
    And user enters valid UK postcode
    And user selects an age range option
    And user taps consent checkbox
    And user taps continue button
    Then success alert should be displayed
    And success alert message should be shown
    And Done button should be visible on success alert
    When user taps Done button
    Then user should be redirected to welcome screen

  # ---- Duplicate waitlist email ---------------------------------------
  @slow_backend
  Scenario: Duplicate waitlist alert shows message and can be dismissed
    Given user is on waiting list registration screen
    When user submits a valid form using an email already on the waitlist
    Then duplicate waitlist alert should be displayed
    Then alert message should be "This email address is already on the waitlist."
    And OK button should be visible on alert
    When user taps OK button
    Then alert should be dismissed
    And user should remain on waiting list registration screen

  Scenario: Submitting duplicate email twice quickly shows a single alert
    Given user is on waiting list registration screen
    When user submits a valid form using an email already on the waitlist tapping continue twice quickly
    Then only one duplicate waitlist alert should be displayed

  # ---- Resilience ------------------------------------------------------
  Scenario: Waiting list registration screen remains stable after app background and resume
    Given user is on waiting list registration screen
    When app is sent to background
    And app is brought to foreground
    Then waiting list registration screen should be displayed

  Scenario: Waiting list registration screen remains stable after orientation change
    Given user is on waiting list registration screen
    When device orientation is changed
    Then waiting list registration screen should be displayed correctly

  # ---- Accessibility & rendering --------------------------------------
  Scenario: Key elements expose accessibility labels
    Given user is on waiting list registration screen
    Then key elements should have accessibility labels

  Scenario: Waiting list registration screen renders core content without clipping
    Given user is on waiting list registration screen
    Then waiting list registration screen should render core content correctly
