// File: discoverCareerPage.mts
import { chromium } from "playwright";

const [company_name] = process.argv.slice(2);
if (!company_name) {
  console.error(
    "❌ Usage: node --loader ts-node/esm discoverCareerPage.mts <company>"
  );
  process.exit(1);
}

function getDomainFromCompany(company: string): string {
  return `${company.toLowerCase().replace(/\s+/g, "")}.com`;
}

async function discoverJobListings(companyName: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const companyDomain = getDomainFromCompany(companyName);
  const searchQuery = `site:${companyDomain} careers jobs`;
  const encodedQuery = encodeURIComponent(searchQuery);
  const searchUrl = `https://www.google.com/search?q=${encodedQuery}&num=10&hl=en`;

  console.log(`\n🔍 Starting search for: "${companyName}"`);
  console.log(`🌐 Domain assumed: ${companyDomain}`);
  console.log(`🔎 Google query: ${searchQuery}`);
  console.log(`🔗 Search URL: ${searchUrl}`);

  await page.goto(searchUrl, { waitUntil: "domcontentloaded" });

  const hrefs = await page.$$eval(
    "a",
    (anchors, domain) =>
      anchors
        .map((a) => a.href)
        .filter(
          (href) =>
            href.includes(domain) &&
            /careers|jobs|positions|openings/i.test(href)
        ),
    companyDomain
  );

  if (hrefs.length === 0) {
    console.log("\n⚠️ No relevant career links found.");
    await browser.close();
    return;
  }

  console.log(`\n🔗 Career-related URLs found:`);
  hrefs.forEach((url, index) => {
    console.log(`${index + 1}. ${url}`);
  });

  const chosenUrl = hrefs[0];
  console.log(`\n✅ Chosen URL to follow: ${chosenUrl}`);

  await page.goto(chosenUrl, { waitUntil: "domcontentloaded" });

  console.log(`📄 Loaded chosen page. URL: ${page.url()}`);
  const pageTitle = await page.title();
  console.log(`🧾 Page Title: ${pageTitle}`);

  // optional: show how many <a>, <div>, etc. on page
  const numLinks = await page.$$eval("a", (els) => els.length);
  const numDivs = await page.$$eval("div", (els) => els.length);
  console.log(`📊 Page Stats: ${numLinks} <a> tags | ${numDivs} <div> tags`);

  await browser.close();
  console.log(
    "\n✅ Done. You can now proceed to extract job listings from this page."
  );
}

discoverJobListings(company_name);
