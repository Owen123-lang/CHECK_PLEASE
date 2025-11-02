import React from 'react';
import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Quick Links */}
          <div>
            <h3 className="text-white font-bold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/dashboard" className="hover:text-yellow-400 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/chat" className="hover:text-yellow-400 transition-colors">
                  Start Chat
                </Link>
              </li>
              <li>
                <a href="#features" className="hover:text-yellow-400 transition-colors">
                  Features
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-yellow-400 transition-colors">
                  Documentation
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-white font-bold mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="hover:text-yellow-400 transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-yellow-400 transition-colors">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-yellow-400 transition-colors">
                  Cookie Policy
                </a>
              </li>
            </ul>
          </div>

          {/* Copyright & Built With */}
          <div>
            <h3 className="text-white font-bold mb-4">Check Please</h3>
            <p className="text-sm mb-4">
              Platform verifikasi profil akademis berbasis AI untuk peneliti dan institusi pendidikan.
            </p>
            <p className="text-xs text-gray-500">
              © 2025 Check Please. All rights reserved.
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Built with Next.js, FastAPI, and Google Gemini AI
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
