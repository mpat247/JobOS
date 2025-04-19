// Path: app/src/designtests/discoverCareerPage.mts

import { chromium } from "playwright";

type SearchResult = {
  title: string;
  url: string;
};

const [company_name, country = ""] = process.argv.slice(2);
if (!company_name) {
  console.error(
    "Usage: node --loader ts-node/esm discoverCareerPage.mts <company> [country]"
  );
  process.exit(1);
}

async function searchGoogle(
  query: string,
  limit = 10
): Promise<SearchResult[]> {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123 Safari/537.36",
    locale: "en-CA",
  });
  const page = await context.newPage();

  try {
    const encoded_query = encodeURIComponent(query);
    const url = `https://www.google.com/search?q=${encoded_query}&num=${limit}&hl=en&gl=CA`;

    // go directly to the SERP and wait for network idle
    await page.goto(url, { waitUntil: "networkidle" });

    // grab every <h3> and its nearest <a>
    const results = await page.$$eval(
      "h3",
      (heads, max) =>
        (heads as HTMLElement[])
          .map((h) => {
            const link = h.closest("a");
            return link
              ? {
                  title: h.innerText.trim(),
                  url: (link as HTMLAnchorElement).href,
                }
              : null;
          })
          .filter((r) => r !== null)
          .slice(0, max as number),
      limit
    );

    return results as SearchResult[];
  } finally {
    await browser.close();
  }
}

export async function findCareerPages(company: string, location = "") {
  const query = `${company} careers site ${location} job openings`.trim();
  console.log(`🔎 Running search: "${query}"\n`);

  const results = await searchGoogle(query, 15);

  const career_sites = results
    .filter(
      ({ title, url }) =>
        /(careers|jobs|work|join|vacancies)/i.test(title) ||
        /(careers|jobs)/i.test(url)
    )
    .slice(0, 5);

  if (career_sites.length === 0) {
    console.warn("⚠️  No relevant career pages found.");
    return;
  }

  career_sites.forEach(({ title, url }, i) => {
    console.log(`${i + 1}. ${title}\n   ${url}\n`);
  });
}

findCareerPages(company_name, country);
