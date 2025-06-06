"use client";

import React, { useState, useEffect } from "react";
import { useChat, UseChatOptions } from "@ai-sdk/react"
import { Chat } from "@/components/ui/chat";
import { ModelSelector, type Model } from "@/components/ui/model-selector";
import { Hyperparameters } from "./ui/hyperparameter-form";

type ChatDemoProps = {
  initialMessages?: UseChatOptions["initialMessages"];
  hyperparameters?: Hyperparameters;
};

export function ChatDemo(props: ChatDemoProps) {
  // estados para los modelos
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");

  // 1) cargar lista de modelos al montar
  useEffect(() => {
    fetch("/api/chat/ollama/models")
      .then((res) => res.json())
      .then((data) => {
        console.log("models API response:", data);
        // Si data es un array, úsalo; si trae .models, úsalo; sino, []
        const modelsArray: Model[] = Array.isArray(data)
          ? data
          : data.models ?? [];
        setModels(modelsArray);
        if (modelsArray.length > 0) {
          setSelectedModel(modelsArray[0].name);
          console.log("selectedModel", modelsArray[0].name);
        }
      })
      .catch(console.error);
  }, []);

  // 2) hook de chat, inyectando el modelo seleccionado en el body
  const { messages, input, handleInputChange, append, stop, isLoading } =
    useChat({
      ...props,
      api: "/api/chat/ollama",
      body: { model: selectedModel },
    });

  const handleChatSubmit = (
    event?: { preventDefault?: () => void }
  ) => {
    if (event && event.preventDefault) {
      event.preventDefault();
    }

    if (!input.trim()) return;

    // Append the user's message to the chat
    append({ role: "user", content: input });

    console.log("Sending request with data:", {
      model: selectedModel,
      messages: [...messages, { role: "user", content: input }],
    });

    fetch("/api/chat/ollama", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: selectedModel,
        messages: [...messages, { role: "user", content: input }],
      }),
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Failed to fetch response from API");
          return;
        }
        return response.json();
      })
      .then((data) => {
        if (data?.response) {
          // Append the LLM's response to the chat
          append({ role: "assistant", content: data.response });
        }
      })
      .catch((error) => {
        console.error("Error during chat submission:", error);
      });
  };

  return (
    <div className="flex flex-col h-[500px] w-full space-y-4">
      {/* Botón / modal para elegir modelo */}
      <ModelSelector
        models={models}
        selected={selectedModel}
        onSelect={setSelectedModel}
      />

      {/* UI de chat */}
      <Chat
        className="grow"
        messages={messages}
        handleSubmit={handleChatSubmit}
        input={input}
        handleInputChange={handleInputChange}
        isGenerating={isLoading}
        stop={stop}
        append={append}
        suggestions={[
          "Generame un contrato formal entre 2 partes.",
          "Generame un reporte de ventas generadas por varios vendedores.",
          "Generame una baja de un empleado por enfermedad.",
        ]}
      />
    </div>
  );
}