"use client";

import { useState } from "react";
import {
    SignInButton,
    SignUpButton,
    SignOutButton,
    SignedIn,
    SignedOut,
    UserButton,
} from "@clerk/nextjs";
import Link from "next/link";

export default function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    // Common button animation classes
    const buttonBaseClasses = "transition-all duration-300 transform hover:scale-105";
    const primaryButtonClasses = `${buttonBaseClasses} px-5 py-2.5 text-sm font-medium rounded-lg`;
    const secondaryButtonClasses = `${buttonBaseClasses} px-5 py-2.5 text-sm font-medium rounded-lg`;
    const mobileButtonClasses = `${buttonBaseClasses} block w-full text-center px-5 py-2.5 text-sm font-medium`;

    return (
        <nav className="bg-gray-950 border-b border-gray-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <div className="flex-shrink-0">
                        <Link href="/" className="flex items-center hover:scale-105 transition-transform duration-300">
                            <span className="text-white text-xl font-bold tracking-tight">
                                Web Beautifier
                            </span>
                        </Link>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="flex md:hidden">
                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className={`text-gray-100 hover:text-white focus:outline-none ${buttonBaseClasses}`}
                        >
                            <svg
                                className="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                {isMenuOpen ? (
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M6 18L18 6M6 6l12 12"
                                    />
                                ) : (
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M4 6h16M4 12h16M4 18h16"
                                    />
                                )}
                            </svg>
                        </button>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {/* Auth Section */}
                        <div className="ml-6 flex items-center space-x-4">
                            <SignedOut>
                                <SignInButton>
                                    <button className={`${secondaryButtonClasses} bg-black text-pink-500 border border-pink-500 hover:bg-pink-500 hover:text-white hover:border-transparent`}>
                                        Log in
                                    </button>
                                </SignInButton>
                                <SignUpButton>
                                    <button className={`${primaryButtonClasses} bg-black text-white hover:bg-pink-600`}>
                                        Sign up
                                    </button>
                                </SignUpButton>
                            </SignedOut>

                            <SignedIn>
                                <UserButton afterSignOutUrl="/" />
                                <SignOutButton>
                                    <button className={`${secondaryButtonClasses} text-gray-300 border border-gray-700 hover:bg-gray-800`}>
                                        Sign out
                                    </button>
                                </SignOutButton>
                            </SignedIn>
                        </div>
                    </div>
                </div>

                {/* Mobile Menu */}
                {isMenuOpen && (
                    <div className="md:hidden bg-gray-900">
                        <div className="px-2 pt-4 pb-3 border-t border-gray-800 space-y-2">
                            <SignedOut>
                                <SignInButton>
                                    <button className={`${mobileButtonClasses} bg-black text-pink-500 border border-pink-500 rounded-lg hover:bg-pink-500 hover:text-white`}>
                                        Log in
                                    </button>
                                </SignInButton>
                                <SignUpButton>
                                    <button className={`${mobileButtonClasses} bg-black text-white rounded-lg hover:bg-pink-600`}>
                                        Sign up
                                    </button>
                                </SignUpButton>
                            </SignedOut>

                            <SignedIn>
                                <div className="flex justify-between items-center px-3">
                                    <UserButton afterSignOutUrl="/" />
                                    <SignOutButton>
                                        <button className={`${buttonBaseClasses} ml-4 px-4 py-2 text-sm font-medium text-gray-300 border border-gray-700 rounded-lg hover:bg-gray-800`}>
                                            Sign out
                                        </button>
                                    </SignOutButton>
                                </div>
                            </SignedIn>
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}