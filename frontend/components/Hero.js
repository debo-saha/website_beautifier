import React from "react";
import Spline from "@splinetool/react-spline/next";
import Link from "next/link";
export default function Home() {
  return (
    <>
      <main className="min-h-screen bg-black text-white">
        <section className="relative h-screen flex items-center justify-center overflow-hidden">
          {/* Spline Background */}
          <div className="absolute inset-0 w-full h-[70vh] md:h-full">
            <Spline
              className="w-full h-full hidden md:block"
              scene="https://prod.spline.design/WNmhHpS4PLU16Rji/scene.splinecode"
            />
            {/* Fallback for mobile or if Spline fails to load */}
            <div className="w-full h-full bg-gray-900 md:hidden flex items-center justify-center">
              <p className="text-gray-400 text-center">
                Spline scene is available on desktop devices.
              </p>
            </div>
          </div>

          {/* Text Overlay */}
          <div className="relative z-10 text-center px-4">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              Welcome Web Beautification Arena
            </h1>
            <p className="text-lg md:text-xl text-gray-300 mb-6 max-w-2xl mx-auto">
              Discover an immersive experience powered by cutting-edge visuals
              and innovative design.
            </p>
            <div className="flex justify-center space-x-4">
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-full transform transition-all duration-300 hover:scale-105">
                <Link href="/beautify">
                Get Started
                </Link>
              </button>
              <button className="border border-purple-500 text-purple-300 hover:bg-purple-500/10 px-8 py-3 rounded-full transform transition-all duration-300 hover:scale-105">
                Learn More
              </button>
            </div>
          </div>
        </section>
    
        
      </main>
    </>
  );
}