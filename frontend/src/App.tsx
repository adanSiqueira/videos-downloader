import { useState } from "react";
import { downloadVideo } from "./services/api";

export default function GlassDownloader() {
  const [url, setUrl] = useState("");
  const [cookiesFile, setCookiesFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadLink, setDownloadLink] = useState("");

  const handleDownload = async () => {
    if (!url) {
      setError("Please enter a valid URL");
      return;
    }

    setLoading(true);
    setError("");
    setDownloadLink("");

    try {
      const formData = new FormData();
      formData.append("url", url);

      if (cookiesFile) {
        formData.append("cookies", cookiesFile);
      }

      const data = await downloadVideo(formData);

      const fullUrl = `https://stream-video-downloader.onrender.com${data.download_url}`;

      setDownloadLink(fullUrl);
      window.open(fullUrl, "_blank");

    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-950 via-red-600 to-red-500 flex flex-col items-center px-4">

      {/* Main Card */}
      <div className="w-full max-w-xl rounded-2xl bg-white/10 backdrop-blur-lg p-8 shadow-xl border border-white/20 ring-1 ring-black mt-12">

        <h1 className="text-4xl font-bold text-white text-center mb-6">
          Web Videos Downloader
        </h1>

        <p className="text-white/80 text-center mb-8">
          Download any video from web! Paste your link and download in seconds.
        </p>

        <div className="flex flex-col gap-4">

          {/* URL Input */}
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="w-full rounded-lg bg-white/20 px-4 py-3 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white"
          />

          <p className="text-white/80 text-center mt-3 justify-items-start">
          Select your cookies file (.txt or .json)
          </p>

          {/* File Input */}
            <div className="flex justify-center">
              <input
                type="file"
                accept=".txt,.json"
                onChange={(e) => setCookiesFile(e.target.files?.[0] || null)}
                className=" text-white text-sm file:mr-4 file:py-2 file:px-4 mb-6 file:rounded-lg file:border-0 file:bg-white file:text-black hover:file:bg-gray-200"
              />
            </div>

          {/* Button */}
          <button
            onClick={handleDownload}
            disabled={loading}
            className="w-full rounded-lg bg-white text-black font-semibold py-3 hover:bg-gray-200 transition disabled:opacity-50"
          >
            {loading ? "Downloading..." : "Download Video"}
          </button>

          {/* Error */}
          {error && (
            <p className="text-red-200 text-sm text-center">{error}</p>
          )}

          {/* Download Link */}
          {downloadLink && (
            <a
              href={downloadLink}
              target="_blank"
              className="text-white underline text-center text-sm"
            >
              Click here if download didn’t start
            </a>
          )}
        </div>
      </div>

      {/* Accordion */}
      <div className="w-full max-w-xl mt-6">
        <details className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl p-4 text-white cursor-pointer">
          
          <summary className="font-semibold text-lg outline-none">
            Why do I need a cookie file and how to get it?
          </summary>

          <div className="mt-4 text-sm text-white/80 space-y-4">

            {/* Why section */}
            <div>
              <h3 className="font-semibold text-white text-base mb-1">
                🔐 Why do I need a cookie file?
              </h3>
              <p>
                Some YouTube videos require authentication to confirm that the request
                is coming from a real user and not a bot.
              </p>
              <p>
                To download these videos, you must provide a <strong>cookie file</strong>,
                which allows the downloader to use <em>your YouTube session</em>.
              </p>
              <p className="text-white/60 mt-2">
                🔒 Your login information is never stored.
              </p>
            </div>

          {/* Browsers */}
            <div className="space-y-2">

              {/* EDGE */}
              <details className="bg-white/5 rounded-lg p-3">
                <summary className="cursor-pointer font-semibold">
                  Microsoft Edge
                </summary>

                <div className="mt-3 space-y-3">
                  <ol className="list-decimal list-inside space-y-2">

                    <li>
                      Install extension:
                      <br />
                      <a
                        href="https://microsoftedge.microsoft.com/addons/detail/j2team-cookies/lmakhegealefmkbnagibiebebncemhgn"
                        target="_blank"
                        className="underline text-blue-200"
                      >
                        J2TEAM Cookies
                      </a>
                    </li>

                    <li>Open YouTube and login</li>

                    <li>
                      Click the extension → Export → "Export as File"
                    </li>

                    <li>Upload the file here</li>

                  </ol>
                </div>
              </details>

              {/* CHROME */}
              <details className="bg-white/5 rounded-lg p-3">
                <summary className="cursor-pointer font-semibold">
                  Google Chrome
                </summary>

                <div className="mt-3 space-y-3">
                  <ol className="list-decimal list-inside space-y-2">

                    <li>
                      Install extension:
                      <br />
                      <a
                        href="https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
                        target="_blank"
                        className="underline text-blue-200"
                      >
                        Get cookies.txt LOCALLY
                      </a>
                    </li>

                    <li>Open YouTube and login</li>

                    <li>
                      Click extension → Export cookies (.txt or .json)
                    </li>

                    <li>Upload the file here</li>

                  </ol>
                </div>
              </details>

              {/* FIREFOX */}
              <details className="bg-white/5 rounded-lg p-3">
                <summary className="cursor-pointer font-semibold">
                  Mozilla Firefox
                </summary>

                <div className="mt-3 space-y-3">
                  <ol className="list-decimal list-inside space-y-2">

                    <li>
                      Install extension:
                      <br />
                      <a
                        href="https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/"
                        target="_blank"
                        className="underline text-blue-200"
                      >
                        cookies.txt (Firefox Add-on)
                      </a>
                    </li>

                    <li>Open YouTube and login</li>

                    <li>
                      Click extension → Export cookies
                    </li>

                    <li>Upload the file here</li>

                  </ol>
                </div>
              </details>

              {/* SAFARI */}
              <details className="bg-white/5 rounded-lg p-3">
                <summary className="cursor-pointer font-semibold">
                  Safari
                </summary>

                <div className="mt-3 space-y-3">
                  <p>
                    Safari has limited support for cookie export extensions.
                  </p>

                  <ol className="list-decimal list-inside space-y-2">
                    <li>
                      Recommended: Use Chrome, Edge, or Firefox instead
                    </li>
                    <li>
                      Advanced: Export cookies manually using developer tools
                    </li>
                  </ol>

                </div>
              </details>

            </div>

</div>
        </details>
      </div>

    </div>
  );
}