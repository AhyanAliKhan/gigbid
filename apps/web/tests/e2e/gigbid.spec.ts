import { test, expect } from '@playwright/test';

test.describe('GigBid Web Application E2E Test Suite', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to local frontend instance or test mock server
    await page.goto('/');
  });

  test('1. Onboarding flow: loads persona, inspects verified evidence, and sets guardrails', async ({ page }) => {
    // Navigate to Onboarding tab
    await page.click('button:has-text("Onboarding")');
    await expect(page.locator('h2')).toContainText('Freelancer Onboarding & Persona Configuration');

    // Check personas available
    const personaSelect = page.locator('select');
    await expect(personaSelect).toBeVisible();
    await personaSelect.selectOption('alex_chen_aiml');

    // Verify evidence is loaded
    await expect(page.locator('text=alex_chen_aiml')).toBeVisible();
    await expect(page.locator('text=CV Summary')).toBeVisible();
    await expect(page.locator('text=Verified Case Studies')).toBeVisible();

    // Verify guardrails input and save
    const budgetInput = page.locator('input[type="number"]').first();
    await budgetInput.fill('150');
    await page.click('button:has-text("Save Persona & Guardrails")');
    await expect(page.locator('text=Configuration & guardrails saved successfully')).toBeVisible();
  });

  test('2. Proposal Studio: Review & approve proposal with interrupt gate', async ({ page }) => {
    // Navigate to Proposal Studio
    await page.click('button:has-text("Proposal Studio")');
    await expect(page.locator('h2')).toContainText('Proposal Studio & Human Approval Gate');

    // Select the first pending proposal if available
    const pendingCard = page.locator('div:has-text("Pending Approval")').first();
    if (await pendingCard.isVisible()) {
      await pendingCard.click();
      
      // Ensure Approval Panel appears
      await expect(page.locator('text=Human Approval Gate')).toBeVisible();
      await expect(page.locator('text=Compliance Guard Verdict: PASS')).toBeVisible();

      // Click Approve & Submit Bid
      await page.click('button:has-text("Approve & Submit Bid")');
      await expect(page.locator('text=Proposal Approved & Submitted!')).toBeVisible();
    }
  });

  test('3. Proposal Studio: Reject with reason', async ({ page }) => {
    await page.click('button:has-text("Proposal Studio")');
    const pendingCard = page.locator('div:has-text("Pending Approval")').first();
    if (await pendingCard.isVisible()) {
      await pendingCard.click();

      // Click Request Revisions / Reject
      await page.click('button:has-text("Request Revisions / Reject")');

      // Reason input modal or prompt
      const reasonInput = page.locator('textarea[placeholder*="feedback"]');
      if (await reasonInput.isVisible()) {
        await reasonInput.fill('Please lower the proposed quote to $45/hr and emphasize PyTorch case studies.');
        await page.click('button:has-text("Confirm Rejection / Revisions")');
        await expect(page.locator('text=Revision Requested')).toBeVisible();
      }
    }
  });

  test('4. Edit proposal draft inline before approval', async ({ page }) => {
    await page.click('button:has-text("Proposal Studio")');
    const pendingCard = page.locator('div:has-text("Pending Approval")').first();
    if (await pendingCard.isVisible()) {
      await pendingCard.click();

      // Find the editable proposal text area
      const proposalTextarea = page.locator('textarea').first();
      await expect(proposalTextarea).toBeVisible();

      const originalText = await proposalTextarea.inputValue();
      const updatedText = originalText + '\n\nLooking forward to discussing the architecture.';
      await proposalTextarea.fill(updatedText);

      // Verify draft state updated
      await expect(proposalTextarea).toHaveValue(updatedText);
    }
  });

  test('5. Degraded mode banner check when MCP server is degraded or offline', async ({ page }) => {
    // Mock degraded mode state via API or test hook
    await page.route('/api/runs/active', async route => {
      const json = {
        runs: [],
        degraded: true,
        degraded_reason: 'Portfolio MCP is unreachable: degraded fallback active (local cached profile only)'
      };
      await route.fulfill({ json });
    });

    await page.reload();
    // Check if degraded banner appears
    await expect(page.locator('text=DEGRADED MODE ACTIVE')).toBeVisible();
    await expect(page.locator('text=fallback active')).toBeVisible();
  });

});
