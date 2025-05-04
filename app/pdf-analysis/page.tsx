"use client";
import React, { useState } from "react";
import { PDFChat } from "@/components/pdf-chat";
import { Settings, BookOpen, FileText } from "lucide-react";
import { Hyperparameters } from "@/components/ui/hyperparameter-form";

export default function PDFAnalysisPage() {
  const [hyperparams,] = useState<Hyperparameters>({
    temperature: 0.5, // Más bajo para respuestas más precisas en análisis legal
    top_p: 0.9,
    max_tokens: 2048, // Mayor cantidad para análisis detallado
  });
  
  const [showSettings, setShowSettings] = useState(false);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfContent, setPdfContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = async (file: File) => {
    if (!file || !file.name.endsWith('.pdf')) {
      alert('Por favor, sube un archivo PDF válido');
      return;
    }

    setIsLoading(true);
    setPdfFile(file);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/pdf/extract', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setPdfContent(data.text);
      } else {
        console.error('Error al extraer texto del PDF');
        alert('Error al procesar el PDF. Inténtalo de nuevo.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al procesar el PDF');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)]">
      {/* Sidebar */}
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
            <FileText className="h-4 w-4 text-[#9e2a2b]" />
            <h3 className="font-medium text-sm text-gray-800">Análisis de Documentos</h3>
          </div>
          <p className="text-sm text-gray-600">
            Sube un documento PDF para que CertyLex lo analice, identifique mejoras y proporcione recomendaciones legales basadas en fuentes oficiales.
          </p>
        </div>
        
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

      {/* Main content area - FIXED */}
      <div className="flex-1 flex flex-col h-full overflow-auto">
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

        {/* PDF chat container */}
        <div className="flex-1 overflow-auto bg-white">
          <div className="min-h-full flex flex-col">
            <div className="p-4 border-b border-gray-200 bg-[#f5f5f5]">
              <h3 className="text-lg font-medium text-[#9e2a2b]">Análisis de Documentos Legales</h3>
              <p className="text-sm text-gray-600">Sube un documento PDF para obtener análisis y mejoras</p>
            </div>
            
            <div className="flex-1 p-4">
              <PDFChat 
                pdfFile={pdfFile}
                pdfContent={pdfContent}
                isLoading={isLoading}
                onFileUpload={handleFileUpload}
                hyperparameters={hyperparams}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
