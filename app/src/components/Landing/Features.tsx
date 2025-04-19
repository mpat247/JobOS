// src/components/Landing/Features.tsx
import React from "react";

const features = [
  { title: "Browse Jobs", desc: "Explore listings without signing up." },
  { title: "Save Favorites", desc: "Bookmark jobs you love." },
  { title: "Get Notified", desc: "Receive email alerts on new matches." },
];

export default function Features() {
  return (
    <section className="py-16 bg-caribbean-50">
      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((f) => (
          <div key={f.title} className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-xl font-semibold text-caribbean-600 mb-2">
              {f.title}
            </h3>
            <p className="text-gray-700">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
