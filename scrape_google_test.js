const { chromium } = require('playwright-extra');
const fs = require('fs');
const stealth = require('puppeteer-extra-plugin-stealth')();
const randomUseragent = require('random-useragent');
const path = require('path');
const { parse } = require('json2csv');

chromium.use(stealth);

// Read proxies from file
const proxies = fs.readFileSync('proxies.txt', 'utf-8').split('\n').filter(Boolean);

function parseProxy(proxyStr) {
    const [server, port, username, password] = proxyStr.split(':');
    return {
        server: `${server}:${port}`,
        username,
        password
    };
}

function getRandomProxy() {
    const proxyStr = proxies[Math.floor(Math.random() * proxies.length)];
    return parseProxy(proxyStr);
}

function convertResultsToCSV(results) {
    const headers = ['Restaurant', 'Name', 'Link'];
    const rows = results.flatMap(result => 
        result.links.map(link => [
            result.restaurant,
            link.name,
            link.href
        ])
    );

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');

    return csvContent;
}

function getRandomUserAgent() {
    const userAgent = randomUseragent.getRandom(ua => {
        return (ua.osName === 'Windows' || ua.osName === 'Mac OS' || ua.osName === 'Linux') &&
               (ua.userAgent.includes('en-US') || ua.userAgent.includes('en-GB'));
    });
    return userAgent;
}

process.stdin.setEncoding('utf8');

let input = '';

process.stdin.on('data', chunk => {
  input += chunk;
});

process.stdin.on('end', async () => {
    const { restaurantNames, typeNames, outputPath } = JSON.parse(input);
  
    const results = [];
  
    for (let count = 0; count < restaurantNames.length; count++) {
      const restaurant = restaurantNames[count];
      const typeRestaurant = typeNames[count];
      const proxy = getRandomProxy();
  
      const browser = await chromium.launch({
        headless: true,
        proxy: {
          server: proxy.server,
          username: proxy.username,
          password: proxy.password,
        }
      });
  
      const query = `${typeRestaurant}: ${restaurant} manager, director linkedin uk`;
      const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=10`;
  
      const context = await browser.newContext({
        userAgent: getRandomUserAgent(),
        viewport: { width: 1280, height: 800 }
      });
  
      const page = await context.newPage();
  
      await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1'
      });
  
      await page.route('**/*', (route) => {
        const request = route.request();
        if (['image', 'stylesheet', 'font', 'media', 'script'].includes(request.resourceType())) {
          route.abort();
        } else {
          route.continue();
        }
      });
  
      page.on('response', async (response) => {
        const data = await response.body().catch(() => Buffer.from([]));
      });
  
      try {
        await page.goto(searchUrl, { waitUntil: 'load', timeout: 15000 });
  
        const isCaptcha = await page.evaluate(() => {
          return document.querySelector('div#captcha') !== null || document.querySelector('form[action="/sorry/index"]') !== null;
        });
  
        if (isCaptcha) {
          console.log('CAPTCHA detected, skipping this search');
          await context.close();
          await browser.close();
          continue; 
        }
  
        await new Promise(resolve => setTimeout(resolve, Math.floor(Math.random() * 3000) + 1000));
  
        const links = await page.evaluate(() => {
          return Array.from(document.querySelectorAll('a')).map(anchor => ({
            href: anchor.href,
            text: anchor.closest('div').innerText || anchor.textContent || anchor.innerText
          }));
        });
  
        const filteredLinks = links.filter(link => {
          const urlMatch = link.href && link.href.includes('linkedin.com') && !link.href.includes('job') && !link.href.includes('company') && !link.href.includes('posts');;
          const restaurantNameMatch = new RegExp(`\\b${restaurant.replace(/\s+/g, '\\s*')}\\b`, 'i').test(link.text);
          return urlMatch && restaurantNameMatch;
        }).map(link => {
          const nameMatch = link.text.match(/^[\w\s.-]+(?=\s+-\s+)/);
          const name = nameMatch ? nameMatch[0].trim() : '';
          return {
            href: link.href,
            name: name,
          };
        });
  
        results.push({
          restaurant,
          links: filteredLinks
        });
      } catch (error) {
        console.error(`Error during search for ${restaurant}: ${error.message}`);
      } finally {
        await context.close();
        await browser.close();
      }
  
      await new Promise(resolve => setTimeout(resolve, Math.floor(Math.random() * 4000) + 4000));
    }
  
    const csvContent = convertResultsToCSV(results);
    fs.writeFileSync(outputPath, csvContent);
  
    console.log(outputPath);
  });