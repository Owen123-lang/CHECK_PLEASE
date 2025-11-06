'use client';

import Link from 'next/link';

export default function FeaturesSection() {
  return (
    <section id="features" className="py-12 sm:py-16 lg:py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-[1600px] mx-auto">
        {/* Section Title with Decorative Lines */}
        <div className="flex items-center justify-center gap-4 lg:gap-6 mb-10 lg:mb-14">
          <div className="w-[60px] sm:w-[100px] lg:w-[200px] h-[3px] lg:h-[4px] bg-white" />
          <h2 className="text-white text-[28px] sm:text-[36px] lg:text-[46px] font-bold text-center whitespace-nowrap">
            Our Features
          </h2>
          <div className="w-[60px] sm:w-[100px] lg:w-[200px] h-[3px] lg:h-[4px] bg-white" />
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8 mb-10 lg:mb-12">
          {/* Feature 1: AI-Based Search */}
          <div className="bg-white rounded-[20px] border-[3px] lg:border-[4px] border-[#FF0000] p-6 lg:p-8 flex flex-col items-center text-center min-h-[340px] lg:min-h-[380px] hover:shadow-2xl hover:shadow-[#FF0000]/30 transition-all duration-300 hover:scale-105 group">
            {/* Icon */}
            <div className="w-[90px] h-[90px] lg:w-[110px] lg:h-[110px] mb-4 lg:mb-6 text-[#FF0000] group-hover:scale-110 transition-transform duration-300">
              <svg viewBox="0 0 24 24" fill="none" className="w-full h-full">
                <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2" />
                <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M11 8C12.6569 8 14 9.34315 14 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>

            {/* Title */}
            <h3 className="text-[#FF0000] text-[22px] lg:text-[26px] font-bold leading-tight mb-3 lg:mb-4">
              Pencarian Berbasis AI
            </h3>

            {/* Description */}
            <p className="text-[#FF0000] text-[15px] lg:text-[17px] font-medium leading-relaxed">
              Ajukan pertanyaan pada Asisten AI kami untuk menemukan profil akademisi, 
              publikasi, dan topik riset secara instan.
            </p>
          </div>

          {/* Feature 2: Latest Data */}
          <div className="bg-white rounded-[20px] border-[3px] border-[#FF0000] p-6 lg:p-8 flex flex-col items-center text-center min-h-[340px] lg:min-h-[380px] hover:shadow-2xl hover:shadow-[#FF0000]/30 transition-all duration-300 hover:scale-105 group">
            {/* Icon */}
            <div className="w-[90px] h-[90px] lg:w-[120px] lg:h-[120px] mb-4 lg:mb-6 text-[#FF0000] group-hover:scale-110 transition-transform duration-300">
              <svg viewBox="0 0 24 24" fill="none" className="w-full h-full">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>

            {/* Title */}
            <h3 className="text-[#FF0000] text-[22px] lg:text-[26px] font-bold leading-tight mb-3 lg:mb-4">
              Data Paling Baru
            </h3>

            {/* Description */}
            <p className="text-[#FF0000] text-[15px] lg:text-[17px] font-medium leading-relaxed">
              Informasi profil selalu up-to-date, memastikan Anda mendapatkan data publikasi 
              dan afiliasi terbaru secara akurat.
            </p>
          </div>

          {/* Feature 3: Save to File */}
          <div className="bg-white rounded-[20px] border-[3px] border-[#FF0000] p-6 lg:p-8 flex flex-col items-center text-center min-h-[340px] lg:min-h-[380px] hover:shadow-2xl hover:shadow-[#FF0000]/30 transition-all duration-300 hover:scale-105 group md:col-span-2 lg:col-span-1">
            {/* Icon */}
            <div className="w-[90px] h-[90px] lg:w-[110px] lg:h-[110px] mb-4 lg:mb-6 text-[#FF0000] group-hover:scale-110 transition-transform duration-300">
              <svg viewBox="0 0 24 24" fill="none" className="w-full h-full">
                <path
                  d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>

            {/* Title */}
            <h3 className="text-[#FF0000] text-[22px] lg:text-[26px] font-bold leading-tight mb-3 lg:mb-4">
              Simpan Profil ke File
            </h3>

            {/* Description */}
            <p className="text-[#FF0000] text-[15px] lg:text-[17px] font-medium leading-relaxed">
              Simpan dan bagikan profil akademisi secara lengkap dalam format PDF 
              yang rapi dan profesional.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
