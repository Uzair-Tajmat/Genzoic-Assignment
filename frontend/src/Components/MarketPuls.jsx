import { useState } from "react";
import {
  Send,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import ReactJson from "react-json-view";

const MarketPulse = () => {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [showFullResponse, setShowFullResponse] = useState(false);

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!ticker.trim()) return;

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      // Mock API call - replace with actual endpoint
      // const mockResponse = {
      //   ticker: ticker.toUpperCase(),
      //   as_of: new Date().toISOString().split("T")[0],
      //   momentum: {
      //     returns: [-0.3, 0.4, 1.1, -0.2, 0.7],
      //     score: 0.34,
      //   },
      //   news: [
      //     {
      //       title: `${ticker.toUpperCase()} unveils new AI initiatives`,
      //       description:
      //         "Company announces breakthrough in artificial intelligence technology...",
      //       url: "https://example.com/news1",
      //     },
      //     {
      //       title: `Strong earnings report for ${ticker.toUpperCase()}`,
      //       description: "Quarterly results exceed analyst expectations...",
      //       url: "https://example.com/news2",
      //     },
      //   ],
      //   pulse: "bullish",
      //   llm_explanation: `Momentum is moderately positive (0.34) and recent headlines highlight product launches and strong earnings performance for ${ticker.toUpperCase()}; hence bullish outlook for tomorrow.`,
      // };

      // // Simulate API delay
      // await new Promise((resolve) => setTimeout(resolve, 1500));
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/market-pulse?ticker=${ticker}`
      );
      const data = await response.json();

      setResponse(data);
    } catch (err) {
      setError("Failed to fetch market pulse. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getPulseColor = (pulse) => {
    switch (pulse) {
      case "bullish":
        return "text-green-600";
      case "bearish":
        return "text-red-600";
      case "neutral":
        return "text-gray-600";
      default:
        return "text-gray-600";
    }
  };

  const getPulseIcon = (pulse) => {
    switch (pulse) {
      case "bullish":
        return <TrendingUp className="w-5 h-5" />;
      case "bearish":
        return <TrendingDown className="w-5 h-5" />;
      case "neutral":
        return <Minus className="w-5 h-5" />;
      default:
        return <Minus className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4">
            <h1 className="text-xl font-semibold">Market-Pulse</h1>
            <p className="text-blue-100 text-sm">
              Get bullish, bearish, or neutral signals for any stock
            </p>
          </div>

          {/* Chat Interface */}
          <div className="p-6 space-y-6">
            {/* Input Form */}
            <div className="flex gap-2">
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                placeholder="Enter stock ticker (e.g., AAPL, MSFT, NVDA)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit(e)}
              />
              <button
                onClick={handleSubmit}
                disabled={loading || !ticker.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                {loading ? "Analyzing..." : "Send"}
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
                {error}
              </div>
            )}

            {/* Response */}
            {response && (
              <div className="space-y-4">
                {/* Main Response Card */}
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="font-semibold text-gray-700">
                      Market Pulse for {response.ticker}
                    </span>
                    <div
                      className={`flex items-center gap-1 ${getPulseColor(
                        response.pulse
                      )}`}
                    >
                      {getPulseIcon(response.pulse)}
                      <span className="font-medium capitalize">
                        {response.pulse}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-800 leading-relaxed">
                    {response.llm_explanation}
                  </p>
                  <div className="mt-2 text-sm text-gray-500">
                    Analysis as of {response.as_of}
                  </div>
                </div>

                {/* Expandable Full Response */}
                <div className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => setShowFullResponse(!showFullResponse)}
                    className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50"
                  >
                    <span className="font-medium text-gray-700">
                      Full Response Details
                    </span>
                    {showFullResponse ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </button>
                  {showFullResponse && (
                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                      <ReactJson
                        src={response}
                        name={false}
                        collapsed={1}
                        enableClipboard={false}
                        displayDataTypes={false}
                        displayObjectSize={false}
                        style={{ fontSize: "0.875rem" }} // text-sm
                      />
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm mt-6">
          Enter a stock ticker to get Market sentiment analysis
        </div>
      </div>
    </div>
  );
};

export default MarketPulse;
