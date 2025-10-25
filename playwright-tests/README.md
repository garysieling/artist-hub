# Playwright Tests for Artist Development Hub

This directory contains end-to-end tests using Playwright.

## Setup

Tests are already set up! Playwright and browsers have been installed.

## Running Tests

```bash
# Run all tests in headless mode
npm test

# Run tests with UI (interactive mode)
npm run test:ui

# Run tests with browser visible
npm run test:headed

# Run tests in debug mode
npm run test:debug

# View test report
npm run test:report
```

## Available Tests

### Google Photos Integration Test

**File:** `google-photos-integration.spec.js`

Tests the Google Photos integration flow:
1. ✓ Load the home page
2. ✓ Navigate to the admin page
3. ✓ Check Google Photos authentication status
4. ✓ Test authentication flow (if not authenticated)
5. ✓ Verify Google File Picker loads successfully
6. ✓ API health checks

## Test Configuration

The Playwright configuration (`playwright.config.js`) includes:

- **Base URL:** http://localhost:3000
- **Test timeout:** 60 seconds
- **Screenshots:** Captured on failure
- **Videos:** Retained on failure
- **Reports:** HTML report in `test-results/html/`

### Auto-start Servers

The configuration will automatically start both backend and frontend servers if they're not already running:

- Backend: http://localhost:3001
- Frontend: http://localhost:3000

You can disable this by setting `reuseExistingServer: false` in `playwright.config.js`.

## Writing New Tests

Create new test files with the `.spec.js` extension:

```javascript
const { test, expect } = require('@playwright/test');

test('my new test', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toContainText('Artist Development Hub');
});
```

## Tips

- Use `test.step()` to organize test steps for better reporting
- Add console.log statements to track test progress
- Use `--headed` mode for debugging visual issues
- Check `test-results/html/` for detailed test reports

## Troubleshooting

**Tests fail with "Cannot connect":**
- Make sure backend is running on port 3001
- Make sure frontend is running on port 3000
- Check that proxy in frontend/package.json points to port 3001

**Google Photos tests skip authentication:**
- OAuth credentials need to be uploaded first via the Admin panel
- See main CLAUDE.md for Google Photos setup instructions
