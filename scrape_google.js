const { chromium } = require('playwright-extra');
const fs = require('fs');
const stealth = require('puppeteer-extra-plugin-stealth')();
const randomUseragent = require('random-useragent');

chromium.use(stealth);

// Read proxies from file
const proxies = fs.readFileSync('proxies.txt', 'utf-8').split('\n').filter(Boolean);

const restaurantNames = fs.readFileSync('places_2_500.txt', 'utf-8').split('\n');

const typeNames = fs.readFileSync('type_2_500.txt', 'utf-8').split('\n');

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

(async () => {
    function delay(time) {
        return new Promise(resolve => setTimeout(resolve, time));
    }

    function getRandomUserAgent() {
        const userAgent = randomUseragent.getRandom(ua => {
            return (ua.osName === 'Windows' || ua.osName === 'Mac OS' || ua.osName === 'Linux') &&
                   (ua.userAgent.includes('en-US') || ua.userAgent.includes('en-GB'));
        });
        return userAgent;
    }

    const results = [];
    let totalDataUsage = 0;
    let count = 0;

    for (const restaurant of restaurantNames) {
        const typeRestaurant = typeNames[count];
        const proxy = getRandomProxy();

        console.log(count);
        console.log(proxy.password);

        // Launch a browser
        const browser = await chromium.launch({
            headless: true,
            proxy: {
                server: proxy.server,
                username: proxy.username,
                password: proxy.password,
            }
        });


        count++;

        const query = `${typeRestaurant}: ${restaurant} manager or director linkedin uk`;
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=10`;

        const context = await browser.newContext({
            userAgent: getRandomUserAgent(),
            viewport: { width: 1280, height: 800 }
        });
        const page = await context.newPage();

        // Add custom headers to the page
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
            totalDataUsage += data.length;
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

            await delay(Math.floor(Math.random() * 3000) + 1000);

        

            const links = await page.evaluate(() => {
                return Array.from(document.querySelectorAll('a')).map(anchor => ({
                    href: anchor.href,
                    text: anchor.closest('div').innerText || anchor.textContent || anchor.innerText
                }));
            });

            // Filter links to include only LinkedIn, exclude job postings, and match the restaurant name and job titles
            const filteredLinks = links.filter(link => {
                const urlMatch = link.href && link.href.includes('linkedin.com') && !link.href.includes('job') && !link.href.includes('company');
                const restaurantNameMatch = new RegExp(`\\b${restaurant.replace(/\s+/g, '\\s*')}\\b`, 'i').test(link.text);
                return urlMatch && restaurantNameMatch;
            }).map(link => {
                const nameMatch = link.text.match(/^[\w\s.-]+(?=\s+-\s+)/);
                const name = nameMatch ? nameMatch[0].trim() : 'Name not found';
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

        await delay(Math.floor(Math.random() * 4000) + 4000);
    }

    const csvContent = convertResultsToCSV(results);
    fs.writeFileSync('results_2_500.csv', csvContent);

    console.log(JSON.stringify(results, null, 2));
    console.log(`Total data usage for ${restaurantNames.length} searches: ${totalDataUsage / 1024} KB`);
})();