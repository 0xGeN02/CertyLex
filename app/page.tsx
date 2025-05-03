"use client";
import React, { useState } from "react";
import { ChatDemo } from "@/components/chat-demo";
import { HyperparameterForm, Hyperparameters } from "@/components/ui/hyperparameter-form";
import { Settings, Info, BookOpen } from "lucide-react";

export default function Home() {
  const [hyperparams, setHyperparams] = useState<Hyperparameters>({
    temperature: 0.7,
    top_p: 1.0,
    max_tokens: 1024,
  });
  
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="flex h-[calc(100vh-8rem)]">
      {/* Sidebar with BOE-style */}
      <div 
        className={`${
          showSettings ? "block" : "hidden"
        } md:block w-full md:w-80 lg:w-96 border-r border-gray-200 bg-[#f5f5f5] p-4 shrink-0 h-full overflow-y-auto transition-all duration-300`}
      >
        <div className="sticky top-0 pb-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[#9e2a2b] flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Configuración
            </h2>
            <button 
              onClick={() => setShowSettings(false)}
              className="md:hidden p-2 rounded-md hover:bg-gray-200 text-gray-700"
            >
              <span>×</span>
            </button>
          </div>
        </div>
        
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Info className="h-4 w-4 text-[#9e2a2b]" />
            <h3 className="font-medium text-sm text-gray-800">Información</h3>
          </div>
          <p className="text-sm text-gray-600">
            Consulta información legal basada en fuentes oficiales como el BOE (Boletín Oficial del Estado).
          </p>
        </div>
        
        <HyperparameterForm values={hyperparams} onChange={setHyperparams} />
        
        <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="h-4 w-4 text-[#9e2a2b]" />
            <h3 className="font-medium text-sm text-gray-800">Fuentes Consultadas</h3>
          </div>
          <ul className="text-sm text-gray-600 list-disc pl-5 space-y-1">
            <li>Boletín Oficial del Estado</li>
            <li>Código Civil Español</li>
            <li>Ley General Tributaria</li>
            <li>Leyes Orgánicas del Estado</li>
          </ul>
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Mobile settings toggle */}
        <div className="md:hidden flex items-center p-3 border-b">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-md hover:bg-gray-100 flex items-center gap-2"
          >
            <Settings className="h-4 w-4 text-[#9e2a2b]" />
            <span className="text-sm font-medium">{showSettings ? "Ocultar Configuración" : "Mostrar Configuración"}</span>
          </button>
        </div>

        {/* Chat container */}
        <div className="flex-1 overflow-hidden bg-white">
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-gray-200 bg-[#f5f5f5]">
              <h3 className="text-lg font-medium text-[#9e2a2b]">Asistente Legal CertyLex</h3>
              <p className="text-sm text-gray-600">Asistente legal con acceso a información oficial del estado español</p>
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