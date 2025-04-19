"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { supabase } from "@/lib/supabaseBrowser";

export default function DashboardPage() {
  const router = useRouter();
  const [showRemember, setShowRemember] = useState(false);
  const [rememberChecked, setRememberChecked] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();

      if (!data.session) {
        router.push("/auth/login");
      } else {
        setUserEmail(data.session.user.email ?? null);

        const rememberMe = localStorage.getItem("rememberMe");
        if (!rememberMe) {
          setShowRemember(true);
        }
      }
    };

    checkSession();
  }, [router]);

  const handleConfirmRemember = () => {
    if (rememberChecked) {
      localStorage.setItem("rememberMe", "true");
      setShowRemember(false);
    }
  };

  return (
    <div className="min-h-screen bg-white p-8">
      <h1 className="text-3xl font-bold text-caribbean-700 mb-4">
        Welcome to JobOS
      </h1>

      {userEmail && (
        <p className="text-gray-700 mb-6">You are logged in as {userEmail}</p>
      )}

      {showRemember && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-lg max-w-sm w-full">
            <h2 className="text-xl font-semibold mb-3">Stay signed in?</h2>
            <p className="mb-4 text-sm text-gray-700">
              Would you like to stay signed in for 30 days on this device?
            </p>

            <div className="flex items-center mb-4">
              <input
                id="rememberMe"
                type="checkbox"
                className="mr-2 h-4 w-4 text-caribbean-600 border-gray-300 rounded focus:ring-caribbean-500"
                onChange={(e) => setRememberChecked(e.target.checked)}
              />
              <label htmlFor="rememberMe" className="text-sm text-gray-700">
                Remember me
              </label>
            </div>

            <button
              onClick={handleConfirmRemember}
              disabled={!rememberChecked}
              className={`w-full px-4 py-2 rounded text-white transition ${
                rememberChecked
                  ? "bg-caribbean-600 hover:bg-caribbean-700"
                  : "bg-gray-300 cursor-not-allowed"
              }`}
            >
              Confirm
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
