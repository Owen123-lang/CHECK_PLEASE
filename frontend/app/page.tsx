import LandingHeader from '@/components/landing/LandingHeader';
import HeroSection from '@/components/landing/HeroSection';
import FeaturesSection from '@/components/landing/FeaturesSection';
import Footer from '@/components/landing/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#1A1E21]">
      <LandingHeader />
      <HeroSection />
      <FeaturesSection />
      <Footer />
    </main>
  );
}
