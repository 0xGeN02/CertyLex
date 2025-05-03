"use client";
import React, { useState } from "react";
import { ChatDemo } from "@/components/chat-demo";
import { HyperparameterForm, Hyperparameters } from "@/components/ui/hyperparameter-form";

export default function Home() {
  const [hyperparams, setHyperparams] = useState<Hyperparameters>({
    temperature: 0.7,
    top_p: 1.0,
    max_tokens: 1024,
  });
  
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="flex h-[calc(100vh-8rem)]">
      {/* Sidebar for settings (collapsible on mobile) */}
      <div 
        className={`${
          showSettings ? "block" : "hidden"
        } md:block w-full md:w-80 lg:w-96 border-r bg-white p-4 shrink-0 h-full overflow-y-auto transition-all duration-300`}
      >
        <div className="sticky top-0 pb-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Settings</h2>
            <button 
              onClick={() => setShowSettings(false)}
              className="md:hidden p-2 rounded-md hover:bg-gray-100"
            >
              <span>×</span>
            </button>
          </div>
        </div>
        <HyperparameterForm values={hyperparams} onChange={setHyperparams} />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Mobile settings toggle */}
        <div className="md:hidden flex items-center p-3 border-b">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-md hover:bg-gray-100"
          >
            <span className="text-sm font-medium">{showSettings ? "Hide Settings" : "Show Settings"}</span>
          </button>
        </div>

        {/* Chat container */}
        <div className="flex-1 overflow-hidden bg-white rounded-lg">
          <div className="h-full flex flex-col">
            <div className="p-4 border-b">
              <h3 className="text-lg font-medium">CertyLex Assistant</h3>
              <p className="text-sm text-gray-500">Legal AI assistant powered by advanced language models</p>
            </div>
            
            <div className="flex-1 p-4">
              <ChatDemo hyperparameters={hyperparams} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}