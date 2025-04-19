import { supabase } from "@/lib/supabaseBrowser";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) console.error("Login error:", error.message);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <button
        onClick={handleLogin}
        className="bg-caribbean-500 hover:bg-caribbean-600 text-white font-semibold py-2 px-6 rounded-lg shadow"
      >
        Sign in with Google
      </button>
    </div>
  );
}
