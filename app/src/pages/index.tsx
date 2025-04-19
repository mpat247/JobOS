"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Layout/Header";
import Hero from "@/components/Landing/Hero";
import Features from "@/components/Landing/Features";
import { supabase } from "@/lib/supabaseBrowser";

export default function LandingPage() {
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header session={session} />
      <Hero />
      <Features />
    </div>
  );
}
