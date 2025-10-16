"use client";

import { useEffect, useState } from "react";
import { getSites, getStatus, addSite } from "../lib/api";

export default function Home() {
  const [sites, setSites] = useState<any[]>([]);
  const [newUrl, setNewUrl] = useState("");
  const [message, setMessage] = useState("");

  const loadSites = async () => {
    const data = await getSites();
    setSites(data);
  };

  useEffect(() => {
    loadSites();
  }, []);

  const handleAdd = async () => {
    if (!newUrl) {
      setMessage("Please enter a URL");
      return;
    }
    try {
      await addSite(newUrl);
      setNewUrl("");
      setMessage("Site added successfully");
      loadSites();
    } catch (err) {
      setMessage("Failed to add site. Use a valid full URL like https://example.com");
    }
  };

  const handleCheck = async (id: number) => {
    const res = await getStatus(id);
    setMessage(
      `${res.url} → ${res.online ? "🟢 Online" : "🔴 Offline"} (${res.response_time_ms.toFixed(
        1
      )} ms)`
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      {/* HEADER */}
      <header className="border-b border-gray-800 bg-gray-950 px-8 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">
          Tolu’s <span className="text-blue-400">StatusPulse</span>
        </h1>
        <span className="text-sm text-gray-400">v1.0</span>
      </header>

      {/* MAIN */}
      <main className="flex-grow p-8 max-w-3xl mx-auto w-full">
        <div className="flex gap-2 mb-6">
          <input
            type="url"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            placeholder="https://example.com"
            className="border border-gray-700 bg-gray-800 text-gray-100 px-3 py-2 flex-grow rounded-md placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleAdd}
            className="bg-green-500 hover:bg-green-600 text-white px-4 rounded-md"
          >
            Add
          </button>
        </div>

        {message && (
          <p className="mb-4 text-gray-400 transition-all duration-300">
            {message}
          </p>
        )}

        <div className="grid gap-4">
          {sites.map((site) => (
            <div
              key={site.id}
              className="bg-gray-800 p-4 rounded-xl flex justify-between items-center border border-gray-700 hover:border-blue-600 transition-colors"
            >
              <div>
                <p className="font-semibold text-blue-400">{site.url}</p>
                <p className="text-sm text-gray-500">
                  Added {new Date(site.created_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => handleCheck(site.id)}
                className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-md"
              >
                Check
              </button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
