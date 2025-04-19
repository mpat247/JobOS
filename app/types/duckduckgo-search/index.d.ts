// app/src/types/duckduckgo-search/index.d.ts
declare module "duckduckgo-search" {
  export interface DuckDuckGoTextResult {
    title: string;
    href: string;
    body: string;
  }

  export interface DuckDuckGoImageResult {
    title: string;
    image: string;
    thumbnail: string;
    url: string;
    height: number;
    width: number;
    source: string;
  }

  export interface DuckDuckGoSearchApi {
    /** Web results (async iterator) */
    text(
      query: string,
      region?: string,
      safeSearch?: "on" | "moderate" | "off",
      timeLimit?: string | null
    ): AsyncGenerator<DuckDuckGoTextResult>;

    /** Image results (async iterator) */
    images(
      query: string,
      region?: string,
      safeSearch?: "on" | "moderate" | "off"
    ): AsyncGenerator<DuckDuckGoImageResult>;
  }

  const api: DuckDuckGoSearchApi;
  export default api;
}
