import { createBrowserClient } from "@supabase/ssr";
console.log(
  "Supabase URL: ",
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  "Supabase Anon Key: ",
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export const createSupabaseClient = () =>
  createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
