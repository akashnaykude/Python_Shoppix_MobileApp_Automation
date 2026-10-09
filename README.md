# Shoppix MobileApp Automation

Phase-1 scaffold for Android automation using Python, Appium, pytest and pytest-bdd.

## Scope
- Login (valid and invalid)

## Stack
- Python + Appium
- pytest + pytest-bdd
- POM style pages
- JSON based profiles and data
- Allure reporting

## Folder layout
- Features/: Gherkin feature files
- Steps/: pytest-bdd step bindings
- src/core/: config, driver, utilities
- src/pages/: page objects
- configs/profiles/: execution profiles
- Data/Login/: test data templates
- artifacts/: screenshots and allure outputs

## Notes
- APK is resolved from latest dated folder under:
  C:/Users/akash.naykude/source/Shoppix android Build APKs
- APK filename expected: Shoppix.apk
- Real credentials should be provided via .env only.

## Implemented phase-1 flow
- Login validation
- Invalid password alert handling with supported variants:
  - Incorrect email or password entered. Please try again.
  - Please check your password
- Retry login after dismissing alert

## Local setup
1. Install dependencies
   py -m pip install -r requirements.txt
2. Create .env from .env.example and set:
   - SHOPPIX_LOGIN_EMAIL
   - SHOPPIX_LOGIN_PASSWORD
3. Start Appium server on port 4723
4. Connect Android device with adb

## Run commands
- Collect scenarios only:
  py -m pytest --collect-only -q
- Login scenarios:
  py -m pytest Steps/Login_steps.py -q
- Full phase-1 smoke:
  py -m pytest -m smoke -q
