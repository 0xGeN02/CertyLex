"use client";

import React, { useState, useEffect } from "react";
import { useChat, type UseChatOptions } from "ai/react";
import { Chat } from "@/components/ui/chat";
import { ModelSelector, type Model } from "@/components/ui/model-selector";

type ChatDemoProps = {
  initialMessages?: UseChatOptions["initialMessages"];
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
        setModels(data.models);
        if (data.models.length > 0) {
          setSelectedModel(data.models[0].name);
        }
      })
      .catch(console.error);
  }, []);

  // 2) hook de chat, inyectando el modelo seleccionado en el body
  const { messages, input, handleInputChange, handleSubmit, append, stop, isLoading } =
    useChat({
      ...props,
      body: { model: selectedModel },
    });

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
        handleSubmit={handleSubmit}
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