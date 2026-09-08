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
test('charts reconcile comparable statements and cash movements', async ({page})=>{
 await page.goto('/');
 await page.getByRole('button',{name:'Explore DEMO DATA'}).click();
 await expect(page.getByRole('img',{name:'Revenue and operating cash flow by fiscal period'})).toBeVisible();
 await expect(page.getByRole('img',{name:'Opening to closing cash reconciliation'})).toBeVisible();
 await expect(page.getByText('Net income → operating cash flow',{exact:true})).toBeVisible();
});
test('offline imports and evidence exports recalculate; bad files clear output',async({page,request},testInfo)=>{
 const demo=await (await request.get('/api/demo')).json();
 await page.goto('/');
 await page.locator('#file').setInputFiles({name:'companyfacts.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(demo.companyfacts))});
 await page.getByRole('button',{name:'Analyze statements'}).click();
 await expect(page.getByText('USER PROVIDED DATA',{exact:true})).toBeVisible();
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'Export evidence package'}).click();
 const download=await downloadPromise;
 const exported=testInfo.outputPath('evidence.json');await download.saveAs(exported);
 await page.locator('#file').setInputFiles(exported);
 await page.getByRole('button',{name:'Analyze statements'}).click();
 await expect(page.getByText('Cash behind earnings',{exact:true})).toBeVisible();
 await page.locator('#file').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{bad')});
 await expect(page.locator('#error')).not.toBeEmpty();
 await expect(page.getByText('Cash behind earnings',{exact:true})).toHaveCount(0);
});
