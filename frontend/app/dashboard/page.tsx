'use client';

import React from 'react';
import Link from 'next/link';
import LandingHeader from "@/components/landing/LandingHeader";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { Plus, BookOpen } from 'lucide-react';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="bg-black min-h-screen text-white">
        <LandingHeader />
      
      <main className="max-w-6xl mx-auto px-4 py-12">
        {/* Page Title */}
        <h1 className="text-3xl md:text-4xl font-bold text-yellow-400 mb-8">
          Your Notebooks
        </h1>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Create New */}
          <Link 
            href="/chat"
            className="bg-gray-800 rounded-lg p-6 flex flex-col items-center justify-center border-2 border-dashed border-gray-600 hover:border-yellow-400 transition-colors min-h-[200px] group"
          >
            <Plus className="w-12 h-12 text-gray-400 group-hover:text-yellow-400 transition-colors mb-3" />
            <span className="text-gray-300 group-hover:text-yellow-400 transition-colors font-semibold">
              Create new notebook
            </span>
          </Link>

          {/* Card 2: IoT Communication */}
          <Link 
            href="/chat"
            className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors min-h-[200px] flex flex-col justify-between border border-gray-700 hover:border-yellow-400"
          >
            <div>
              <BookOpen className="w-8 h-8 text-yellow-400 mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">
                IoT Communication
              </h3>
              <p className="text-sm text-gray-400">
                Research on Internet of Things communication protocols
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-700">
              <p className="text-xs text-gray-500">
                Last edited: 2 days ago
              </p>
            </div>
          </Link>

          {/* Card 3: TP7 */}
          <Link 
            href="/chat"
            className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors min-h-[200px] flex flex-col justify-between border border-gray-700 hover:border-yellow-400"
          >
            <div>
              <BookOpen className="w-8 h-8 text-yellow-400 mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">
                TP7
              </h3>
              <p className="text-sm text-gray-400">
                Technical Paper 7: Advanced AI Systems
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-700">
              <p className="text-xs text-gray-500">
                Last edited: 1 week ago
              </p>
            </div>
          </Link>

          {/* Card 4: Machine Learning */}
          <Link 
            href="/chat"
            className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors min-h-[200px] flex flex-col justify-between border border-gray-700 hover:border-yellow-400"
          >
            <div>
              <BookOpen className="w-8 h-8 text-yellow-400 mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">
                Machine Learning
              </h3>
              <p className="text-sm text-gray-400">
                Deep learning and neural networks study
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-700">
              <p className="text-xs text-gray-500">
                Last edited: 3 weeks ago
              </p>
            </div>
          </Link>
        </div>

        {/* Empty State Message (optional) */}
        <div className="mt-12 text-center">
          <p className="text-gray-500 text-sm">
            Click on any notebook to continue your research, or create a new one to get started.
          </p>
        </div>
      </main>
      </div>
    </ProtectedRoute>
  );
}
