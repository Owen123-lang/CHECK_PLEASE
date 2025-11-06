'use client';

import Link from 'next/link';

export default function Footer() {
  return (
    <footer id="about" className="bg-gradient-to-b from-white to-gray-50 pt-12 sm:pt-16 lg:pt-20 pb-6 lg:pb-8 border-t-4 border-[#FF0000]">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        {/* Logo and Description Section */}
        <div className="mb-8 lg:mb-12 pb-8 border-b-2 border-gray-200">
          <img 
            src="/CheckPlease.svg" 
            alt="Check Please Logo" 
            className="h-[60px] sm:h-[70px] lg:h-[85px] w-auto mb-4"
          />
          <p className="text-gray-600 text-[14px] lg:text-[16px] max-w-[600px] leading-relaxed">
            Platform pencarian akademisi terlengkap dengan teknologi AI untuk menemukan 
            peneliti, publikasi, dan topik riset secara efisien.
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12 mb-8 lg:mb-10">
          {/* Navigations Column */}
          <div className="space-y-4">
            <h4 className="text-black text-[20px] lg:text-[24px] font-extrabold mb-4 lg:mb-5 relative inline-block">
              Navigations
              <span className="absolute bottom-0 left-0 w-12 h-1 bg-[#FF0000] rounded-full"></span>
            </h4>
            <ul className="space-y-2.5 lg:space-y-3">
              <li className="group">
                <Link href="/login" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Login
                </Link>
              </li>
              <li className="group">
                <Link href="/register" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Register
                </Link>
              </li>
              <li className="group">
                <Link href="/" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Homepage
                </Link>
              </li>
              <li className="group">
                <Link href="/search" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Search
                </Link>
              </li>
              <li className="group">
                <Link href="#about" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  About Us
                </Link>
              </li>
              <li className="group">
                <Link href="#features" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Features
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal Column */}
          <div className="space-y-4">
            <h4 className="text-black text-[20px] lg:text-[24px] font-extrabold mb-4 lg:mb-5 relative inline-block">
              Legal
              <span className="absolute bottom-0 left-0 w-12 h-1 bg-[#FF0000] rounded-full"></span>
            </h4>
            <ul className="space-y-2.5 lg:space-y-3">
              <li className="group">
                <Link href="/terms" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Terms &amp; Services
                </Link>
              </li>
              <li className="group">
                <Link href="/privacy" className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-all duration-300 flex items-center gap-2">
                  <span className="w-0 h-0.5 bg-[#FF0000] group-hover:w-3 transition-all duration-300"></span>
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Us Column */}
          <div className="space-y-4">
            <h4 className="text-black text-[20px] lg:text-[24px] font-extrabold mb-4 lg:mb-5 relative inline-block">
              Contact Us
              <span className="absolute bottom-0 left-0 w-12 h-1 bg-[#FF0000] rounded-full"></span>
            </h4>
            
            {/* Contact Info */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-gray-700 text-[14px] lg:text-[16px]">
                <svg className="w-5 h-5 text-[#FF0000]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" />
                </svg>
                <a href="mailto:contact@checkplease.com" className="hover:text-[#FF0000] transition-colors">
                  contact@checkplease.com
                </a>
              </div>
            </div>

            {/* Social Media Icons */}
            <div className="pt-2">
              <p className="text-gray-600 text-[13px] lg:text-[14px] mb-3 font-medium">Follow Us</p>
              <div className="flex gap-3">
                {/* Email Icon */}
                <a
                  href="mailto:contact@checkplease.com"
                  className="w-[36px] h-[36px] lg:w-[40px] lg:h-[40px] bg-gray-100 rounded-full flex items-center justify-center text-gray-700 hover:bg-[#FF0000] hover:text-white transition-all duration-300 hover:scale-110 shadow-md"
                  aria-label="Email"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] lg:w-[20px] lg:h-[20px]">
                    <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" />
                  </svg>
                </a>

                {/* LinkedIn Icon */}
                <a
                  href="https://linkedin.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-[36px] h-[36px] lg:w-[40px] lg:h-[40px] bg-gray-100 rounded-full flex items-center justify-center text-gray-700 hover:bg-[#0077B5] hover:text-white transition-all duration-300 hover:scale-110 shadow-md"
                  aria-label="LinkedIn"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] lg:w-[20px] lg:h-[20px]">
                    <path d="M19 3A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3H19M18.5 18.5V13.2A3.26 3.26 0 0 0 15.24 9.94C14.39 9.94 13.4 10.46 12.92 11.24V10.13H10.13V18.5H12.92V13.57C12.92 12.8 13.54 12.17 14.31 12.17A1.4 1.4 0 0 1 15.71 13.57V18.5H18.5M6.88 8.56A1.68 1.68 0 0 0 8.56 6.88C8.56 5.95 7.81 5.19 6.88 5.19A1.69 1.69 0 0 0 5.19 6.88C5.19 7.81 5.95 8.56 6.88 8.56M8.27 18.5V10.13H5.5V18.5H8.27Z" />
                  </svg>
                </a>

                {/* Instagram Icon */}
                <a
                  href="https://instagram.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-[36px] h-[36px] lg:w-[40px] lg:h-[40px] bg-gray-100 rounded-full flex items-center justify-center text-gray-700 hover:bg-gradient-to-br hover:from-[#833AB4] hover:via-[#FD1D1D] hover:to-[#F77737] hover:text-white transition-all duration-300 hover:scale-110 shadow-md"
                  aria-label="Instagram"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-[18px] h-[18px] lg:w-[20px] lg:h-[20px]">
                    <path d="M7.8,2H16.2C19.4,2 22,4.6 22,7.8V16.2A5.8,5.8 0 0,1 16.2,22H7.8C4.6,22 2,19.4 2,16.2V7.8A5.8,5.8 0 0,1 7.8,2M7.6,4A3.6,3.6 0 0,0 4,7.6V16.4C4,18.39 5.61,20 7.6,20H16.4A3.6,3.6 0 0,0 20,16.4V7.6C20,5.61 18.39,4 16.4,4H7.6M17.25,5.5A1.25,1.25 0 0,1 18.5,6.75A1.25,1.25 0 0,1 17.25,8A1.25,1.25 0 0,1 16,6.75A1.25,1.25 0 0,1 17.25,5.5M12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9Z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>

          {/* Team Credits Column */}
          <div className="space-y-4">
            <h4 className="text-black text-[20px] lg:text-[24px] font-extrabold mb-4 lg:mb-5 relative inline-block">
              Our Team
              <span className="absolute bottom-0 left-0 w-12 h-1 bg-[#FF0000] rounded-full"></span>
            </h4>
            <div className="space-y-2.5 lg:space-y-3">
              <div className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-colors cursor-pointer">
                Rowen Rodotua Harahap
              </div>
              <div className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-colors cursor-pointer">
                Musyaffa Iman Supriadi
              </div>
              <div className="text-gray-700 text-[14px] lg:text-[16px] font-medium hover:text-[#FF0000] transition-colors cursor-pointer">
                Muhammad Riyan Satrio Wibowo
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 lg:pt-8 border-t-2 border-gray-200">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-gray-600 text-[13px] lg:text-[15px] font-medium">
              © 2025 Check Please. All rights reserved.
            </p>
            <div className="flex items-center gap-4 text-gray-500 text-[12px] lg:text-[14px]">
              <span>Made with ❤️ from Universitas Indonesia</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
