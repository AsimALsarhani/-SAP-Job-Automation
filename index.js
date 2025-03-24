// index.js
const puppeteer = require('puppeteer');
const nodemailer = require('nodemailer');
const config = require('./config.json');

async function runAutomation() {
  let browser;
  try {
    // Launch browser in headless mode (include '--no-sandbox' if required)
    browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
    const page = await browser.newPage();

    // Navigate to the login page and wait until the network is idle
    await page.goto(config.loginUrl, { waitUntil: 'networkidle2' });

    // ---- Sign In ----
    // Wait for the username field to appear and fill it in
    await page.waitForSelector(config.selectors.username, { visible: true });
    await page.type(config.selectors.username, config.credentials.username);
    
    // Wait for the password field to appear and fill it in
    await page.waitForSelector(config.selectors.password, { visible: true });
    await page.type(config.selectors.password, config.credentials.password);

    // Click the sign in button and wait for navigation to complete
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2' }),
      page.click(config.selectors.signInButton),
    ]);

    // ---- UI Interactions ----
    // Scroll to the bottom of the page
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(2000); // Wait 2 seconds for lazy loading if needed

    // Click on the Save button
    await page.waitForSelector(config.selectors.saveButton, { visible: true });
    await page.click(config.selectors.saveButton);

    // Wait for 50 seconds as required
    await page.waitForTimeout(50000);

    // Scroll back up to the top
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(1000);

    // Click on a blank area (using the <body> element)
    await page.click('body');

    // Take a screenshot as proof
    const screenshotPath = 'screenshot.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`Screenshot saved at ${screenshotPath}`);

    // Send the screenshot via email
    await sendEmail(screenshotPath);
    console.log('Automation completed successfully.');
  } catch (error) {
    console.error('Error in automation:', error);
  } finally {
    if (browser) {
      await browser.close();
      console.log('Browser closed.');
    }
  }
}

async function sendEmail(screenshotPath) {
  // Create a transporter object using SMTP transport
  let transporter = nodemailer.createTransport({
    host: config.email.host,
    port: config.email.port,
    secure: config.email.secure, // true for 465, false for other ports
    auth: {
      user: config.email.user,
      pass: config.email.pass,
    },
  });

  // Send mail with defined transport object
  let info = await transporter.sendMail({
    from: `"SAP Automation" <${config.email.user}>`,
    to: config.email.to,
    subject: 'SAP Automation Screenshot Proof',
    text: 'Please find attached the screenshot proof from the latest SAP Automation run.',
    attachments: [
      {
        filename: 'screenshot.png',
        path: screenshotPath,
      },
    ],
  });

  console.log('Email sent:', info.messageId);
}

runAutomation();
