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

  return (
    <main className="flex min-h-screen flex-col items-center justify-center max-w-2xl mx-auto">
      <HyperparameterForm values={hyperparams} onChange={setHyperparams} />
      <div className="border rounded-md p-4 w-full">
        <ChatDemo hyperparameters={hyperparams} />
      </div>
    </main>
  );
}
