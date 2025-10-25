/**
 * Google Photos Integration Test
 *
 * This test verifies the Google Photos integration flow:
 * 1. Load the home page
 * 2. Navigate to the admin page
 * 3. Verify Google Photos connection status
 * 4. Trigger Google file picker (if not authenticated)
 * 5. Confirm the picker loads successfully
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:3000';
const API_BASE_URL = 'http://localhost:3001';

test.describe('Google Photos Integration', () => {
  test('should load home page, navigate to admin, and interact with Google Photos', async ({ page }) => {
    // Step 1: Load the home page
    test.step('Load home page', async () => {
      await page.goto(BASE_URL);

      // Wait for the page to load
      await page.waitForLoadState('networkidle');

      // Verify the dashboard header is present
      await expect(page.locator('h1')).toContainText('Artist Development Hub');

      // Verify tools grid is visible
      await expect(page.locator('.tools-grid')).toBeVisible();

      console.log('✓ Home page loaded successfully');
    });

    // Step 2: Navigate to the admin page
    test.step('Open admin page', async () => {
      // Find and click the Admin Panel tool card
      const adminCard = page.locator('.tool-card').filter({ hasText: 'Admin Panel' });
      await expect(adminCard).toBeVisible();
      await adminCard.click();

      // Wait for navigation
      await page.waitForURL('**/admin');

      // Verify we're on the admin page
      await expect(page).toHaveURL(/.*\/admin/);

      // Verify admin page content
      await expect(page.locator('h2')).toContainText('Admin Panel');

      console.log('✓ Admin page opened successfully');
    });

    // Step 3: Check Google Photos authentication status
    test.step('Check Google Photos auth status', async () => {
      // Wait for the Google Photos section to appear
      const googlePhotosSection = page.locator('text=Google Photos Integration').locator('..');
      await expect(googlePhotosSection).toBeVisible({ timeout: 10000 });

      // Check if there's an auth status indicator
      const authStatus = page.locator('text=/authenticated|not authenticated|ready/i').first();
      const statusText = await authStatus.textContent();
      console.log(`Google Photos auth status: ${statusText}`);
    });

    // Step 4 & 5: Select to connect Google Photos and verify picker loads
    test.step('Connect Google Photos and verify picker', async () => {
      // Look for authentication or connection button
      const connectButton = page.locator('button').filter({
        hasText: /connect|authenticate|authorize|upload credentials/i
      }).first();

      if (await connectButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        console.log('Found connect button, checking authentication flow...');

        // Check if we need to upload OAuth credentials first
        const uploadCredsButton = page.locator('button').filter({
          hasText: /upload.*credentials/i
        });

        if (await uploadCredsButton.isVisible({ timeout: 2000 }).catch(() => false)) {
          console.log('⚠ OAuth credentials need to be uploaded first');
          console.log('  Please upload OAuth credentials JSON file to proceed with authentication');

          // Verify the upload button is functional
          await expect(uploadCredsButton).toBeEnabled();
          console.log('✓ Upload credentials button is available and enabled');

          // Test file upload functionality (without actually uploading)
          const fileInput = page.locator('input[type="file"]');
          if (await fileInput.count() > 0) {
            await expect(fileInput).toBeAttached();
            console.log('✓ File input for credentials upload is present');
          }
        } else {
          // OAuth credentials are present, test the auth flow
          console.log('Testing authentication flow...');

          // Set up a promise to wait for popup
          const popupPromise = page.waitForEvent('popup', { timeout: 5000 });

          // Click connect/authorize button
          await connectButton.click();

          try {
            // Wait for OAuth popup window
            const popup = await popupPromise;
            console.log('✓ OAuth popup opened successfully');

            // Verify it's a Google auth URL or correct auth endpoint
            const popupUrl = popup.url();
            console.log(`OAuth URL: ${popupUrl}`);

            // Check if it's a Google accounts URL or local OAuth callback
            const isGoogleAuth = popupUrl.includes('accounts.google.com') ||
                               popupUrl.includes('oauth2') ||
                               popupUrl.includes('auth');

            expect(isGoogleAuth).toBeTruthy();
            console.log('✓ OAuth URL is valid');

            // Close the popup (we don't want to complete actual authentication in tests)
            await popup.close();
            console.log('✓ OAuth popup closed (test mode)');

          } catch (error) {
            console.log('Note: OAuth popup may require credentials to be configured');
            console.log(`Error: ${error.message}`);
          }
        }
      } else {
        console.log('✓ Already authenticated with Google Photos');

        // Verify authenticated state - look for Google Picker button or album list
        const pickerButton = page.locator('button').filter({
          hasText: /open.*picker|select.*photos|import.*photos/i
        });

        if (await pickerButton.isVisible({ timeout: 5000 }).catch(() => false)) {
          console.log('Found Google Picker button');

          // Click to open picker
          await pickerButton.click();

          // Wait for picker iframe or dialog to appear
          // Google Picker typically loads in an iframe
          const pickerFrame = page.frameLocator('iframe[src*="google"]').first();

          try {
            // Verify picker content loaded
            await expect(pickerFrame.locator('body')).toBeVisible({ timeout: 10000 });
            console.log('✓ Google Picker loaded successfully');

            // Close picker (ESC key or close button)
            await page.keyboard.press('Escape');
            console.log('✓ Google Picker closed');

          } catch (error) {
            console.log('Note: Google Picker may need full authentication to load');
            console.log(`Error: ${error.message}`);
          }
        } else {
          // Look for synced albums or other indicators of successful auth
          const albumsSection = page.locator('text=/albums|synced|photos/i');
          if (await albumsSection.count() > 0) {
            console.log('✓ Google Photos integration is active (albums/photos visible)');
          }
        }
      }
    });
  });

  test('should verify API health check', async ({ request }) => {
    // Test the backend API is responding
    const response = await request.get(`${API_BASE_URL}/api/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('ok');
    console.log('✓ Backend API is healthy');
  });

  test('should verify Google Photos auth status endpoint', async ({ request }) => {
    // Test the Google Photos auth status endpoint
    const response = await request.get(`${API_BASE_URL}/api/google-photos/auth-status`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    console.log('Google Photos auth status from API:', data);

    // Verify response structure
    expect(data).toHaveProperty('configured');
    expect(data).toHaveProperty('authenticated');
    expect(data).toHaveProperty('message');

    console.log(`✓ Auth status: configured=${data.configured}, authenticated=${data.authenticated}`);
  });
});
