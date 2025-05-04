"use client";

import React, { useState } from "react";
import { useChat } from "@ai-sdk/react";
import { Chat } from "@/components/ui/chat";
import { Hyperparameters } from "./ui/hyperparameter-form";
import { FileText, Upload, RefreshCw, CheckCircle, AlertTriangle, FileEdit, MessageSquare, BookOpen } from "lucide-react";

type PDFChatProps = {
  pdfFile: File | null;
  pdfContent: string | null;
  isLoading: boolean;
  onFileUpload: (file: File) => void;
  hyperparameters?: Hyperparameters;
};

type ViewMode = "original" | "improved" | "analysis";

export function PDFChat(props: PDFChatProps) {
  const { pdfFile, pdfContent, isLoading, onFileUpload, hyperparameters } = props;
  const [viewMode, setViewMode] = useState<ViewMode>("original");
  const [analysisResponse, setAnalysisResponse] = useState<{
    improvedDocument: string;
    formattedResponse: string;
  } | null>(null);

  // Set up chat hook for the conversation with PDF content
  const { messages, input, handleInputChange, append, stop, isLoading: isChatLoading } =
    useChat({
      api: "/api/pdf/analyze",
      body: { 
        pdfContent,
        ...hyperparameters
      },
    });

  // Handle file input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  // Handle chat submission
  const handleChatSubmit = (event?: { preventDefault?: () => void }) => {
    if (event && event.preventDefault) {
      event.preventDefault();
    }

    if (!pdfContent || !input.trim()) return;

    // Append user message
    append({ role: "user", content: input });

    // Make API call to analyze PDF with the question
    fetch("/api/pdf/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pdfContent,
        question: input,
        ...hyperparameters
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
        if (data) {
          // Append AI response to chat
          append({ role: "assistant", content: data.formattedResponse });
          
          // Store full analysis
          setAnalysisResponse({
            improvedDocument: data.improvedDocument,
            formattedResponse: data.formattedResponse
          });
          
          // Switch to analysis view when we get a response
          setViewMode("analysis");
        }
      })
      .catch((error) => {
        console.error("Error during analysis:", error);
      });
  };

  // Extract alerts from the improved document
  const extractAlerts = (improvedDoc: string): {type: string, content: string}[] => {
    const alerts = [];
    const regex = /\/\* (ALERTA|NOTA|SUGERENCIAS)[\s\S]*?\*\//g;
    let match;
    
    while ((match = regex.exec(improvedDoc)) !== null) {
      const alertText = match[0];
      const alertTypeMatch = alertText.match(/\/\* (ALERTA|NOTA|SUGERENCIAS)/);
      const type = alertTypeMatch ? alertTypeMatch[1] : "NOTA";
      
      alerts.push({
        type,
        content: alertText.replace(/\/\* (ALERTA|NOTA|SUGERENCIAS)[^]*?\n/, "").replace(/\*\//, "").trim()
      });
    }
    
    return alerts;
  };

  // If no PDF uploaded yet, show upload interface
  if (!pdfFile && !pdfContent) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center p-8">
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center max-w-xl w-full">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">Sube un documento para analizar</h3>
          <p className="mt-2 text-sm text-gray-500">
            Sube un documento PDF para que CertyLex lo analice y te proporcione mejoras y recomendaciones.
          </p>
          <div className="mt-6">
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 cursor-pointer"
            >
              <Upload className="mr-2 h-4 w-4" />
              Seleccionar PDF
              <input id="file-upload" type="file" accept=".pdf" onChange={handleFileInputChange} className="sr-only" />
            </label>
          </div>
        </div>
      </div>
    );
  }

  // If PDF is loading, show loading state
  if (isLoading) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center">
        <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" />
        <p className="mt-4 text-gray-600">Procesando el documento...</p>
      </div>
    );
  }

  // Alerts from improved document
  const alerts = analysisResponse ? extractAlerts(analysisResponse.improvedDocument) : [];

  // PDF is uploaded and processed, show the chat interface with tabs
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full w-full">
      {/* Left panel: Document View */}
      <div className="md:col-span-2 flex flex-col h-full rounded-lg border border-gray-200 overflow-hidden">
        {/* View mode tabs */}
        <div className="bg-gray-50 px-3 py-2 border-b border-gray-200">
          <div className="flex space-x-2">
            <button
              onClick={() => setViewMode("original")}
              className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center ${
                viewMode === "original" 
                  ? "bg-white text-indigo-700 shadow-sm border border-gray-200" 
                  : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
              }`}
            >
              <FileText className="h-4 w-4 mr-1.5" />
              Original
            </button>
            <button
              onClick={() => setViewMode("improved")}
              className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center ${
                viewMode === "improved" 
                  ? "bg-white text-indigo-700 shadow-sm border border-gray-200" 
                  : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
              }`}
              disabled={!analysisResponse}
            >
              <FileEdit className="h-4 w-4 mr-1.5" />
              Con Mejoras
            </button>
            <button
              onClick={() => setViewMode("analysis")}
              className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center ${
                viewMode === "analysis" 
                  ? "bg-white text-indigo-700 shadow-sm border border-gray-200" 
                  : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
              }`}
              disabled={!analysisResponse}
            >
              <BookOpen className="h-4 w-4 mr-1.5" />
              Análisis
            </button>
          </div>
        </div>

        {/* Document display area with proper scrolling - FIXED */}
        <div className="flex-1 overflow-auto">
          <div className="p-4 bg-white min-h-full">
            {viewMode === "original" && (
              <pre className="whitespace-pre-wrap text-sm font-sans">{pdfContent}</pre>
            )}
            
            {viewMode === "improved" && analysisResponse ? (
              <div className="whitespace-pre-wrap text-sm font-sans">
                <div className="p-3 bg-indigo-50 rounded-md mb-4 text-indigo-800">
                  <h3 className="font-medium text-indigo-800 mb-1 flex items-center">
                    <FileEdit className="h-4 w-4 mr-2" /> 
                    Documento con Mejoras Sugeridas
                  </h3>
                  <p className="text-xs">
                    A continuación se muestra el documento con anotaciones y sugerencias de mejora.
                    Las secciones con /* SUGERENCIAS */ contienen recomendaciones específicas.
                  </p>
                </div>
                <div 
                  className="font-mono text-sm whitespace-pre-wrap" 
                  style={{
                    lineHeight: "1.6",
                    color: "#24292e",
                    background: "#f6f8fa",
                    padding: "1rem",
                    borderRadius: "0.375rem"
                  }}
                >
                  {analysisResponse.improvedDocument.split(/\/\* (ALERTA|NOTA|SUGERENCIAS)[\s\S]*?\*\//).map((part, i) => {
                    const isAlert = i % 2 === 1;
                    const alertContent = isAlert ? part : "";
                    
                    if (isAlert) {
                      return null;
                    }
                    
                    return (
                      <React.Fragment key={i}>
                        {part}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            ) : viewMode === "improved" ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Haz una pregunta para recibir mejoras del documento</p>
              </div>
            ) : null}
            
            {viewMode === "analysis" && analysisResponse ? (
              <div className="prose prose-indigo max-w-none">
                <div dangerouslySetInnerHTML={{ 
                  __html: analysisResponse.formattedResponse
                    .replace(/\n/g, "<br>")
                    .replace(/^# (.*?)$/gm, "<h1>$1</h1>")
                    .replace(/^## (.*?)$/gm, "<h2>$1</h2>")
                }} />
              </div>
            ) : viewMode === "analysis" ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Haz una pregunta para recibir un análisis del documento</p>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {/* Right panel: Alerts and Chat - FIXED */}
      <div className="flex flex-col h-full rounded-lg border border-gray-200 overflow-hidden">
        {/* File info */}
        <div className="bg-gray-50 px-3 py-2 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center">
            <FileText className="h-4 w-4 text-indigo-600 mr-2" />
            <span className="text-sm font-medium truncate max-w-[150px]">{pdfFile?.name || "Documento"}</span>
          </div>
          <div className="text-xs text-gray-500">
            {viewMode === "analysis" ? "Análisis" : viewMode === "improved" ? "Mejoras" : "Original"}
          </div>
        </div>

        {/* Alerts section - FIXED */}
        {alerts.length > 0 && (
          <div className="border-b border-gray-200">
            <div className="p-3 bg-indigo-50">
              <h3 className="font-medium text-sm text-indigo-800 mb-1">Puntos clave identificados</h3>
            </div>
            <div className="p-2 space-y-2 max-h-[250px] overflow-y-auto">
              {alerts.map((alert, index) => (
                <div 
                  key={index} 
                  className={`p-3 rounded-md text-sm ${
                    alert.type === "ALERTA" 
                      ? "bg-red-50 text-red-800 border-l-4 border-red-500" 
                      : alert.type === "NOTA" 
                        ? "bg-blue-50 text-blue-800 border-l-4 border-blue-500"
                        : "bg-green-50 text-green-800 border-l-4 border-green-500"
                  }`}
                >
                  <div className="font-medium flex items-center mb-1">
                    {alert.type === "ALERTA" ? (
                      <AlertTriangle className="h-4 w-4 mr-1.5" />
                    ) : alert.type === "NOTA" ? (
                      <BookOpen className="h-4 w-4 mr-1.5" />
                    ) : (
                      <CheckCircle className="h-4 w-4 mr-1.5" />
                    )}
                    {alert.type === "ALERTA" ? "Advertencia" : alert.type === "NOTA" ? "Nota Legal" : "Sugerencia"}
                  </div>
                  <p className="text-xs whitespace-pre-wrap">{alert.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Chat interface - FIXED */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="bg-indigo-50 px-3 py-2 border-b border-gray-200">
            <h3 className="font-medium text-sm text-indigo-800 flex items-center">
              <MessageSquare className="h-4 w-4 mr-1.5" />
              Consulta sobre el documento
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto">
            <Chat
              messages={messages}
              handleSubmit={handleChatSubmit}
              input={input}
              handleInputChange={handleInputChange}
              isGenerating={isChatLoading}
              stop={stop}
              append={append}
              suggestions={[
                "¿Qué mejoras sugieres para este contrato?",
                "Identifica posibles cláusulas abusivas",
                "Resume los puntos principales del documento",
              ]}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
