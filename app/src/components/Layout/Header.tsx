// src/components/Layout/Header.tsx
"use client";

import React from "react";
import { useRouter } from "next/router";
import { supabase } from "@/lib/supabaseBrowser";

export default function Header({ session }: { session: any }) {
  const router = useRouter();

  const handleLogin = () => router.push("/auth/login");
  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  return (
    <header className="bg-caribbean-50 px-6 py-4 shadow-sm">
      <div className="max-w-6xl mx-auto flex items-center justify-between relative">
        <input
          type="search"
          placeholder="Search jobs..."
          className="w-1/4 p-2 border border-caribbean-300 rounded-lg focus:ring-2 focus:ring-caribbean-400"
        />

        <div className="absolute left-1/2 transform -translate-x-1/2 text-5xl font-bold text-caribbean-700">
          JobOS
        </div>

        {session ? (
          <button
            onClick={handleLogout}
            className="bg-caribbean-500 text-white px-4 py-2 rounded hover:bg-caribbean-600"
          >
            Log out
          </button>
        ) : (
          <button
            onClick={handleLogin}
            className="bg-caribbean-500 text-white px-4 py-2 rounded hover:bg-caribbean-600"
          >
            Log in
          </button>
        )}
      </div>
    </header>
  );
}
