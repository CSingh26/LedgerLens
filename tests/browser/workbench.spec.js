const { test, expect } = require('@playwright/test');
test('analyst runs a labeled company model and invalidates stale assumptions', async ({page}) => {
 await page.goto('/');
 await page.getByRole('button',{name:'Explore DEMO DATA'}).click();
 await expect(page.getByText('DEMO DATA — Meridian Tools',{exact:true})).toBeVisible();
 await expect(page.getByText('Cash behind earnings',{exact:true})).toBeVisible();
 await expect(page.locator('#empty')).toBeHidden();
 await expect(page.getByText('Structured filing facts',{exact:true})).toBeVisible();
 await page.getByLabel('Normalized tax rate (%)').fill('30');
 await expect(page.getByText('Cash behind earnings',{exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Analyze statements'}).click();
 await expect(page.getByText('Cash behind earnings',{exact:true})).toBeVisible();
});
