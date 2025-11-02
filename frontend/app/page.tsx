import LandingHeader from "@/components/landing/LandingHeader";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import Footer from "@/components/landing/Footer";

export default function HomePage() {
  return (
    <div className="bg-black min-h-screen text-white">
      <LandingHeader />
      <HeroSection />
      <FeaturesSection />
      <Footer />
    </div>
  );
}
