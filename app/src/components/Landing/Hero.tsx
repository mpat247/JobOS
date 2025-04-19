// src/components/Landing/Hero.tsx
import React from "react";
// import LoginButton from "@/components/LoginButton";

export default function Hero() {
  return (
    <section className="text-center py-20 bg-white">
      <h1 className="text-3xl font-bold text-caribbean-700 mb-4">
        Search Jobs Directly from Company Career Sites
      </h1>
      <div className="mt-8">
        <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
          Browse thousands of jobs. Add company job listings in real time. Sign
          up to save favorites and get alerts.
        </p>
      </div>
    </section>
  );
}
