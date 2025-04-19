import { supabase } from "@/lib/supabaseBrowser";
import { useEffect } from "react";
import { useRouter } from "next/router";

export default function CallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        router.push("/dashboard");
      } else {
        console.error("No session found after login");
        router.push("/auth/login");
      }
    };

    checkSession();
  }, [router]);

  return <p className="text-center mt-20">Signing you in...</p>;
}
