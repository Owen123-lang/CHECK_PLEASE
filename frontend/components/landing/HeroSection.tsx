'use client';

import Link from 'next/link';

export default function HeroSection() {
  return (
    <section className="min-h-screen flex items-center pt-24 lg:pt-32 pb-12 lg:pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-64 h-64 bg-[#FFFF00]/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#FF0000]/5 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="max-w-[1600px] mx-auto w-full relative z-10">
        {/* Main Headline */}
        <h1 className="text-[#FFFF00] text-[32px] sm:text-[42px] md:text-[52px] lg:text-[62px] xl:text-[68px] font-bold leading-tight mb-6 lg:mb-8 animate-in fade-in slide-in-from-bottom duration-700">
          Temukan Peneliti<br className="sm:hidden" /> yang Anda<br className="sm:hidden" /> Butuhkan.
        </h1>

        {/* Subheadline */}
        <p className="text-white text-[16px] sm:text-[18px] md:text-[22px] lg:text-[26px] leading-relaxed mb-8 lg:mb-10 max-w-[1000px] animate-in fade-in slide-in-from-bottom duration-700 delay-200">
          Akses database profil akademisi terlengkap yang diverifikasi dan diperbarui 
          secara otomatis dengan <span className="text-[#FFFF00] font-semibold">Agentic AI</span>.
        </p>

        {/* CTA Button */}
        <Link
          href="/notebooks"
          className="inline-flex items-center gap-3 lg:gap-4 px-6 lg:px-8 py-3 lg:py-4 bg-[#FF0000] text-white text-[18px] lg:text-[24px] font-semibold rounded-[20px] hover:bg-[#D70000] hover:shadow-2xl hover:shadow-[#FF0000]/50 transition-all duration-300 transform hover:scale-105 animate-in fade-in slide-in-from-bottom delay-300 group"
        >
          Get Started
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            className="text-white lg:w-[36px] lg:h-[36px] group-hover:translate-x-2 transition-transform duration-300"
          >
            <path
              d="M5 12H19M19 12L12 5M19 12L12 19"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Link>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 hidden lg:flex flex-col items-center gap-2 animate-bounce">
          <span className="text-white/50 text-sm">Scroll down</span>
          <svg className="w-6 h-6 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>
    </section>
  );
}
