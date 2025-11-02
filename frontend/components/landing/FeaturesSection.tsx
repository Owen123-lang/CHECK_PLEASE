import React from 'react';
import { Search, Database, Download, CheckCircle } from 'lucide-react';

const features = [
  {
    icon: Search,
    title: "AI-Powered Search",
    description: "Cari profil akademisi dengan teknologi AI yang canggih. Dapatkan hasil yang akurat dan relevan dalam sekejap."
  },
  {
    icon: Database,
    title: "Real-Time Database",
    description: "Akses database yang selalu ter-update dengan informasi terkini dari berbagai sumber akademis terpercaya."
  },
  {
    icon: Download,
    title: "Export & Save",
    description: "Simpan hasil pencarian dalam format PDF profesional. Bagikan dengan mudah kepada tim atau klien Anda."
  },
  {
    icon: CheckCircle,
    title: "Kenapa Check Please?",
    description: "Platform verifikasi profil akademis tercepat dan terpercaya. Hemat waktu hingga 90% dalam riset akademis Anda."
  }
];

export default function FeaturesSection() {
  return (
    <section id="features" className="bg-black py-20 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Title */}
        <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-4">
          Fitur Unggulan
        </h2>
        
        {/* Subtitle */}
        <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
          Dirancang untuk membuat penelitian dan verifikasi profil akademis menjadi lebih cepat, 
          akurat, dan efisien.
        </p>

        {/* Feature List */}
        <div className="max-w-4xl mx-auto">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div 
                key={index} 
                className="border-b border-gray-700 py-6 flex items-start gap-4"
              >
                {/* Icon Placeholder */}
                <div className="flex-shrink-0">
                  <Icon className="w-8 h-8 text-yellow-400" />
                </div>
                
                {/* Content */}
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
