"use client";

import { useEffect, useState } from "react";

export default function Page() {
  const [urls, setUrls] = useState(["", "", ""]);
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);

  const handleInputChange = (index, value) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("http://127.0.0.1:5000/capture", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ urls }),
      });

      if (!res.ok) throw new Error("Failed to fetch");

      const json = await res.json();
      setAnalysisData(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-gray-100">
      {/* Full-page Input Section */}
      <div
        className={`min-h-screen ${
          analysisData ? "pt-20" : "flex items-center justify-center"
        }`}
      >
        <form
          onSubmit={handleSubmit}
          className={`space-y-4 mx-auto ${
            analysisData ? "max-w-4xl" : "max-w-2xl w-full px-4"
          }`}
        >
          <div className="space-y-6">
            {urls.map((url, i) => (
              <input
                key={i}
                type="text"
                placeholder={`Website ${i + 1}`}
                value={url}
                onChange={(e) => handleInputChange(i, e.target.value)}
                className="w-full p-4 bg-gray-900 border-2 border-gray-700 rounded-xl
                          focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500
                          transition-all duration-300 hover:border-gray-600 text-gray-100 text-lg
                          shadow-lg"
              />
            ))}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className={`px-8 py-4 font-bold rounded-xl w-full 
                        bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600
                        transition-all duration-300 transform hover:scale-[1.02] shadow-2xl
                        ${isLoading ? "opacity-75 cursor-not-allowed" : ""}`}
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-3">
                <div className="w-5 h-5 border-2 border-white rounded-full animate-spin border-t-transparent" />
                <span className="text-lg">Analyzing...</span>
              </div>
            ) : (
              <span className="text-lg">Submit</span>
            )}
          </button>
        </form>
      </div>

      {error && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 p-4 bg-red-900/50 border border-red-700 rounded-xl animate-pulse">
          <p className="text-red-400">⚠ {error}</p>
        </div>
      )}

      {analysisData && (
        <div className="space-y-12 max-w-7xl mx-auto px-4 pb-20">
          {/* Capture Results Section */}
          <section className="animate-fade-in">
            <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              📸 Capture Results
            </h2>
            <div className="grid gap-6 md:grid-cols-3">
              {analysisData.capture_results.map((result, idx) => (
                <div
                  key={idx}
                  className="bg-gray-900/50 p-6 rounded-2xl border border-gray-800
                            hover:border-purple-500/30 transition-all duration-300"
                >
                  <div className="space-y-3">
                    <p className="text-purple-400 font-mono text-sm">
                      {result.folder}
                    </p>
                    <span
                      className={`inline-block px-3 py-1.5 rounded-lg ${
                        result.status === "success"
                          ? "bg-green-900/50 text-green-400"
                          : "bg-red-900/50 text-red-400"
                      }`}
                    >
                      {result.status}
                    </span>
                    <a
                      href={result.url}
                      className="block text-blue-400 hover:text-blue-300 transition-colors truncate text-lg"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      ↗ {result.url}
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Matching Results Section */}
          <section className="animate-fade-in">
            <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent glow-cyan">
              🧠 Matching Results
            </h2>
            <div className="space-y-12">
              {Object.entries(analysisData.matching_results).map(
                ([siteKey, siteSections]) => (
                  <div
                    key={siteKey}
                    className="bg-gradient-to-br from-gray-900/50 to-gray-900/20 rounded-2xl border border-gray-800 p-8
                            hover:border-cyan-500/30 transition-all duration-300 backdrop-blur-sm"
                  >
                    <h3 className="text-2xl font-bold mb-8 text-cyan-400 glow-cyan">
                      {siteKey.toUpperCase()}
                    </h3>

                    <div className="space-y-10">
                      {Object.entries(siteSections).map(
                        ([sectionKey, sectionData]) => (
                          <div
                            key={sectionKey}
                            className="border-l-4 border-purple-500/50 pl-6 group relative"
                          >
                            <div className="absolute inset-0 bg-purple-500/5 rounded-r-xl -left-6 group-hover:opacity-30 opacity-0 transition-opacity" />

                            <h4 className="text-xl font-semibold capitalize mb-6 text-purple-300">
                              {sectionKey.replace(/_/g, " ")}
                            </h4>

                            {sectionData.captured_image_url && (
                              <div className="mb-10 relative group">
                                <div className="relative rounded-2xl border-2 border-gray-800 shadow-2xl overflow-hidden">
                                  <img
                                    src={sectionData.captured_image_url}
                                    alt={`${siteKey} ${sectionKey}`           
                        }
                                    className="w-full h-80 object-cover transform transition-transform duration-500 hover:scale-105"
                                  />
                                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                                </div>
                              </div>
                            )}

                            {sectionData.top_matches?.length > 0 && (
                              <div className="mb-10">
                                <p className="text-lg font-medium text-gray-400 mb-6">
                                  Top Matches:
                                </p>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                  {sectionData.top_matches.map((match, idx) => (
                                    <div
                                      key={idx}
                                      className="relative cursor-pointer transform transition-transform hover:scale-[1.03]"
                                      onClick={() =>
                                        setSelectedImage(match.url)
                                      }
                                    >
                                      <div className="aspect-auto rounded-2xl border-2 border-gray-800 overflow-hidden shadow-xl">
                                        <img
                                          src={match.url}
                                          alt={`Match ${idx + 1}`}
                                          className="w-full h-full object-cover transition-transform duration-500 hover:scale-110"
                                        />
                                      </div>

                                      <div className="absolute bottom-4 left-4 bg-black/60 px-3 py-1.5 rounded-full text-sm text-white font-medium">
                                        Match #{idx + 1}
                                      </div>
                                      <div className="absolute top-4 right-4 bg-cyan-700/70 px-3 py-1 rounded-full text-xs font-semibold text-white backdrop-blur-sm">
                                        Score: {match.score.toFixed(2)}
                                      </div>

                                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-2xl" />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {sectionData.suggested_text && (
                              <div className="mt-8 bg-gray-800/30 p-6 rounded-2xl border border-gray-700">
                                <p className="text-base font-medium text-gray-400 mb-4">
                                  Suggested Text:
                                </p>
                                <pre className="whitespace-pre-wrap font-mono text-base text-gray-300 bg-gray-900/50 p-4 rounded-xl border border-gray-800 leading-relaxed">
                                  {sectionData.suggested_text}
                                </pre>
                              </div>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )
              )}
            </div>
          </section>
        </div>
      )}

      {/* Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/95 backdrop-blur-2xl z-50 flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-6xl max-h-[90vh] w-full">
            <button
              className="absolute -top-10 right-0 text-gray-400 hover:text-white transition-colors z-50"
              onClick={() => setSelectedImage(null)}
            >
              <svg
                className="w-10 h-10"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
            <img
              src={selectedImage}
              alt="Enlarged preview"
              className="max-w-full max-h-[80vh] object-contain rounded-2xl shadow-3xl border-4 border-gray-800"
            />
          </div>
        </div>
      )}
    </div>
  );
}