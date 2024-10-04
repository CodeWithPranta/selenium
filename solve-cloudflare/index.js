const { chromium } = require('playwright');
const { Solver } = require('@2captcha/captcha-solver');

const solver = new Solver('d52fe3a0bd3f66413f3eef7f5ccb6449');
const proxyServer = 'https://brd.superproxy.io:9222';
const proxyUser = 'brd-customer-hl_6d74c8bf-zone-scraping_browser1';
const proxyPassword = 'b2xp0qn79kih';


const example = async () => {
   const browser = await chromium.launch({
       headless: false,
       devtools: false,
       proxy: { "server": proxyServer, "username": proxyUser, "password": proxyPassword },
   });

   const context = await browser.newContext({ ignoreHTTPSErrors: true });

   const page = await context.newPage();
   await page.addInitScript({ path: './inject.js' });

   page.on('console', async (msg) => {
       const txt = msg.text();
       if (txt.includes('intercepted-params:')) {
           const params = JSON.parse(txt.replace('intercepted-params:', ''));
           console.log(params);

           try {
               console.log(`Solving the captcha...`);
               const res = await solver.cloudflareTurnstile(params);
               console.log(`Solved the captcha ${res.id}`);
               console.log(res);
               await page.evaluate((token) => {
                   cfCallback(token);
               }, res.data);
           } catch (e) {
               console.log(e.err);
               return process.exit();
           }
       } else {
           return;
       }
   });

   await page.goto('https://visa.vfsglobal.com/aze/en/ltp/login');

   await page.waitForTimeout(5000);
   await page.reload({ waitUntil: "networkidle" });
   console.log('Reloaded');

};

example();