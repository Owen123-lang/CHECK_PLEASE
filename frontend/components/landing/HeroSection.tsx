import React from 'react';
import Link from 'next/link';

export default function HeroSection() {
  return (
    <section className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      {/* Badge */}
      <div className="bg-gray-800 text-sm rounded-full px-3 py-1 border border-gray-600 mb-4">
        <span className="text-gray-300">Powered by Agentic AI</span>
      </div>

      {/* Headline */}
      <h1 className="text-5xl md:text-6xl font-bold mb-4">
        Better Call <span className="text-yellow-400">CHECK PLEASE</span>
      </h1>

      {/* Sub-headline */}
      <p className="text-gray-300 text-lg md:text-xl mt-4 max-w-2xl">
        Temukan dan verifikasi profil akademisi dengan mudah menggunakan teknologi AI terdepan. 
        Buat laporan profesional dalam hitungan detik.
      </p>

      {/* Buttons */}
      <div className="mt-8 flex flex-col sm:flex-row gap-4">
        <Link 
          href="/dashboard"
          className="bg-red-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-red-700 transition-colors"
        >
          Mulai Sekarang
        </Link>
        <a 
          href="#features"
          className="text-blue-400 hover:underline font-semibold py-3 px-6"
        >
          Lihat Fitur
        </a>
      </div>
    </section>
  );
}
