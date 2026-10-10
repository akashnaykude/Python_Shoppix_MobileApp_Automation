@registration
Feature: Registration screen

  Scenario: Registration screen loads successfully
    Given user is on registration screen
    Then registration screen should load successfully

  Scenario: App logo is visible on registration screen
    Given user is on registration screen
    Then app logo should be visible

  Scenario: Welcome heading is visible on registration screen
    Given user is on registration screen
    Then welcome heading should be visible

  Scenario: Subtitle text is visible on registration screen
    Given user is on registration screen
    Then subtitle text should be visible

  Scenario: Back button is visible on registration screen
    Given user is on registration screen
    Then back button should be visible

  Scenario: Email field label is visible on registration screen
    Given user is on registration screen
    Then email field label should be visible

  Scenario: Email input placeholder is visible on registration screen
    Given user is on registration screen
    Then email input placeholder should be visible

  Scenario: Create password field label is visible on registration screen
    Given user is on registration screen
    Then create password field label should be visible

  Scenario: Create password input placeholder is visible on registration screen
    Given user is on registration screen
    Then create password input placeholder should be visible

  Scenario: Confirm password field label is visible on registration screen
    Given user is on registration screen
    Then confirm password field label should be visible

  Scenario: Confirm password input placeholder is visible on registration screen
    Given user is on registration screen
    Then confirm password input placeholder should be visible

  Scenario: Referral code label is visible on registration screen
    Given user is on registration screen
    Then referral code label should be visible

  Scenario: Referral code input placeholder is visible on registration screen
    Given user is on registration screen
    Then referral code input placeholder should be visible

  Scenario: Age confirmation checkbox is visible on registration screen
    Given user is on registration screen
    Then age confirmation checkbox should be visible

  Scenario: Terms and Conditions text is visible on registration screen
    Given user is on registration screen
    Then terms and conditions text should be visible

  Scenario: Privacy Policy text is visible on registration screen
    Given user is on registration screen
    Then privacy policy text should be visible

  Scenario: Continue button is visible on registration screen
    Given user is on registration screen
    Then continue button should be visible

  Scenario: Social registration section text is visible on registration screen
    Given user is on registration screen
    Then social registration section text should be visible

  Scenario: Facebook registration button is visible on registration screen
    Given user is on registration screen
    Then Facebook registration button should be visible

  Scenario: User can enter valid email
    Given user is on registration screen
    When user enters valid email address
    Then email input should show entered value

  Scenario: Email field rejects invalid email format
    Given user is on registration screen
    When user enters invalid email address
    Then email format validation message should be displayed

  Scenario: Email field shows required validation when empty
    Given user is on registration screen
    When user leaves email field empty
    And user enters valid create password
    And user enters matching confirm password
    And user taps age confirmation checkbox
    And user taps continue button
    Then email required validation message should be displayed

  Scenario: User can enter create password
    Given user is on registration screen
    When user enters create password
    Then create password input should show masked value

  Scenario: Create password field is masked by default
    Given user is on registration screen
    Then create password should be hidden by default

  Scenario: User can toggle create password visibility on
    Given user is on registration screen
    When user taps create password visibility toggle icon
    Then create password should be visible

  Scenario: User can toggle create password visibility off
    Given user is on registration screen
    When user taps create password visibility toggle icon
    And user taps create password visibility toggle icon again
    Then create password should be hidden

  Scenario: Create password field rejects weak password
    Given user is on registration screen
    When user enters valid email address
    When user enters weak create password
    And user enters matching confirm password
    And user taps age confirmation checkbox
    And user taps continue button
    Then password strength validation message should be displayed

  Scenario: Create password field shows required validation when empty
    Given user is on registration screen
    When user enters valid email address
    When user leaves create password field empty
    And user enters confirm password
    And user taps age confirmation checkbox
    And user taps continue button
    Then create password required validation message should be displayed

  Scenario: User can enter confirm password
    Given user is on registration screen
    When user enters confirm password
    Then confirm password input should show masked value

  Scenario: Confirm password field is masked by default
    Given user is on registration screen
    Then confirm password should be hidden by default

  Scenario: User can toggle confirm password visibility on
    Given user is on registration screen
    When user taps confirm password visibility toggle icon
    Then confirm password should be visible

  Scenario: User can toggle confirm password visibility off
    Given user is on registration screen
    When user taps confirm password visibility toggle icon
    And user taps confirm password visibility toggle icon again
    Then confirm password should be hidden

  Scenario: Confirm password matches create password successfully
    Given user is on registration screen
    When user enters create password
    And user enters matching confirm password
    Then passwords should match successfully

  Scenario: Confirm password mismatch validation is shown
    Given user is on registration screen
    When user enters valid email address
    And user enters create password
    And user enters non matching confirm password
    And user taps age confirmation checkbox
    And user taps continue button
    Then password mismatch validation message should be displayed

  Scenario: User can enter referral code
    Given user is on registration screen
    When user enters referral code
    Then referral code input should show entered value

  Scenario: Age confirmation checkbox can be selected
    Given user is on registration screen
    When user taps age confirmation checkbox
    Then age confirmation checkbox should be selected

  Scenario: Age confirmation checkbox can be deselected
    Given user is on registration screen
    When user taps age confirmation checkbox
    And user taps age confirmation checkbox again
    Then age confirmation checkbox should be deselected

  Scenario: Terms and Conditions link opens correctly
    Given user is on registration screen
    When user taps terms and conditions link
    Then terms and conditions screen should be displayed

  Scenario: Privacy Policy link opens correctly
    Given user is on registration screen
    When user taps privacy policy link
    Then privacy policy screen should be displayed

  Scenario: User can continue with valid registration data
    Given user is on registration screen
    When user enters valid email address
    And user enters valid create password
    And user enters matching confirm password
    And user taps age confirmation checkbox
    And user taps continue button
    Then user should proceed to next registration step

  Scenario: Registration shows already registered email alert
    Given user is on registration screen
    When user enters already registered email address
    And user enters valid create password
    And user enters matching confirm password
    And user taps age confirmation checkbox
    And user taps continue button
    Then already registered alert should be displayed
    When user taps already registered alert OK button

  Scenario: Facebook registration button opens Facebook auth flow
    Given user is on registration screen
    When user taps Facebook registration button
    Then Facebook auth flow should be displayed

  Scenario: Facebook registration cancel returns to registration screen
    Given user is on registration screen
    When user taps Facebook registration button
    And user cancels Facebook registration
    Then registration screen should be displayed

  Scenario: Registration screen remains stable after app background and resume
    Given user is on registration screen
    When app is sent to background
    And app is brought to foreground
    Then registration screen should be displayed

  Scenario: Registration screen remains stable after orientation change
    Given user is on registration screen
    When device orientation is changed
    Then registration screen should be displayed correctly

  Scenario: Registration screen back press behavior is handled correctly
    Given user is on registration screen
    When user presses Android back
    Then user should be navigated as per expected back behavior

  Scenario: Registration screen elements are accessible
    Given user is on registration screen
    Then all visible elements should have accessibility labels

  Scenario: Registration screen layout is not broken on small screen device
    Given user is on registration screen
    Then registration screen should render correctly on small screen device

  Scenario: Registration screen layout is not broken on large screen device
    Given user is on registration screen
    Then registration screen should render correctly on large screen device
