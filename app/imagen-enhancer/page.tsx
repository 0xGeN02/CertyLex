"use client";
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Loader2, Upload, ZoomIn, Image as ImageIcon, SlidersHorizontal } from "lucide-react";
import { toast } from "sonner";
import Image from "next/image";

export default function ImageEnhancerPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [enhancedImageUrl, setEnhancedImageUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingSteps, setProcessingSteps] = useState<string[]>([]);

  // Opciones de procesamiento
  const [scaleFactorValue, setScaleFactorValue] = useState([1.5]);
  const [enhanceContrast, setEnhanceContrast] = useState(true);
  const [applySharpen, setApplySharpen] = useState(true);
  const [autoCrop, setAutoCrop] = useState(true);

  // Detalles de la imagen procesada
  const [metadata, setMetadata] = useState<any>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    if (file) {
      // Validar que sea una imagen
      if (!file.type.startsWith('image/')) {
        toast.error('Por favor, selecciona un archivo de imagen válido');
        return;
      }

      setSelectedFile(file);
      
      // Crear URL para previsualización
      const fileUrl = URL.createObjectURL(file);
      setPreviewUrl(fileUrl);
      
      // Resetear estado de imagen procesada
      setEnhancedImageUrl(null);
      setProcessingSteps([]);
      setMetadata(null);
    }
  };

  const handleProcessImage = async () => {
    if (!selectedFile) {
      toast.error('Por favor, selecciona una imagen primero');
      return;
    }

    try {
      setIsProcessing(true);
      setProcessingSteps(['Preparando imagen...']);

      // Crear FormData para enviar la imagen
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('scale_factor', scaleFactorValue[0].toString());
      formData.append('enhance_contrast', enhanceContrast.toString());
      formData.append('sharpen', applySharpen.toString());
      formData.append('auto_crop_enabled', autoCrop.toString());

      // Enviar imagen a la API
      const response = await fetch('/api/image/enhance', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || 'Error al procesar la imagen');
      }

      const data = await response.json();
      
      // Obtener URL de la imagen procesada del backend
      setEnhancedImageUrl(`http://localhost:5328${data.enhancedImage}`);
      setProcessingSteps(data.processingSteps || []);
      setMetadata(data.metadata || {});
      
      toast.success('¡Imagen procesada con éxito!');
    } catch (error) {
      console.error('Error al procesar la imagen:', error);
      toast.error('Error al procesar la imagen. Por favor, inténtalo de nuevo.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row h-[calc(100vh-8rem)] bg-gray-50">
      {/* Panel de control */}
      <div className="w-full md:w-80 lg:w-96 border-r border-gray-200 bg-[#f5f5f5] p-4 shrink-0 h-full overflow-y-auto">
        <div className="sticky top-0 pb-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[#9e2a2b] flex items-center gap-2">
              <SlidersHorizontal className="h-5 w-5" />
              Ajustes de Imagen
            </h2>
          </div>
        </div>

        {/* Controles */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Factor de Escala
          </label>
          <div className="mb-4">
            <Slider
              value={scaleFactorValue}
              min={1}
              max={4}
              step={0.1}
              onValueChange={setScaleFactorValue}
            />
            <div className="flex justify-between mt-1 text-xs text-gray-500">
              <span>1x</span>
              <span>{scaleFactorValue[0]}x</span>
              <span>4x</span>
            </div>
          </div>

          <div className="space-y-3 mt-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="enhanceContrast"
                checked={enhanceContrast}
                onChange={(e) => setEnhanceContrast(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="enhanceContrast" className="ml-2 block text-sm text-gray-700">
                Mejorar contraste
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="applySharpen"
                checked={applySharpen}
                onChange={(e) => setApplySharpen(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="applySharpen" className="ml-2 block text-sm text-gray-700">
                Aplicar nitidez
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoCrop"
                checked={autoCrop}
                onChange={(e) => setAutoCrop(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="autoCrop" className="ml-2 block text-sm text-gray-700">
                Recorte automático
              </label>
            </div>
          </div>
        </div>

        {/* Subida de archivo */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-center w-full">
            <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-8 h-8 mb-3 text-gray-500" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Haz clic para subir</span> o arrastra una imagen
                </p>
                <p className="text-xs text-gray-500">JPG, PNG o WEBP</p>
              </div>
              <input 
                id="dropzone-file" 
                type="file" 
                className="hidden" 
                accept="image/*"
                onChange={handleFileChange}
              />
            </label>
          </div>
          {selectedFile && (
            <p className="mt-2 text-sm text-gray-600">
              Archivo seleccionado: {selectedFile.name}
            </p>
          )}
        </div>

        {/* Botón de proceso */}
        <div className="mt-4">
          <Button
            className="w-full bg-indigo-600 hover:bg-indigo-700"
            onClick={handleProcessImage}
            disabled={!selectedFile || isProcessing}
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Procesando...
              </>
            ) : (
              <>
                <ZoomIn className="mr-2 h-4 w-4" />
                Mejorar imagen
              </>
            )}
          </Button>
        </div>

        {/* Información de procesamiento */}
        {processingSteps.length > 0 && (
          <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Pasos de procesamiento:</h3>
            <ul className="text-xs text-gray-600 list-disc pl-5 space-y-1">
              {processingSteps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Área de visualización */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-[#f5f5f5]">
          <h3 className="text-lg font-medium text-[#9e2a2b]">Mejora de Imágenes</h3>
          <p className="text-sm text-gray-600">Sube una imagen para mejorar su resolución y calidad</p>
        </div>

        <div className="flex-1 overflow-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Imagen original */}
            <div className="border border-gray-200 rounded-lg p-4 bg-white">
              <div className="flex items-center mb-2">
                <ImageIcon className="h-4 w-4 text-indigo-600 mr-2" />
                <h4 className="font-medium text-sm">Imagen Original</h4>
              </div>
              <div className="h-80 flex items-center justify-center bg-gray-100 rounded-md overflow-hidden">
                {previewUrl ? (
                  <div className="relative w-full h-full">
                    <Image
                      src={previewUrl}
                      alt="Vista previa"
                      fill
                      style={{ objectFit: 'contain' }}
                    />
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No hay imagen seleccionada</p>
                )}
              </div>
              {selectedFile && (
                <div className="mt-2 text-xs text-gray-500">
                  <p>Tamaño: {(selectedFile.size / 1024).toFixed(2)} KB</p>
                  <p>Tipo: {selectedFile.type}</p>
                </div>
              )}
            </div>

            {/* Imagen procesada */}
            <div className="border border-gray-200 rounded-lg p-4 bg-white">
              <div className="flex items-center mb-2">
                <ZoomIn className="h-4 w-4 text-indigo-600 mr-2" />
                <h4 className="font-medium text-sm">Imagen Mejorada</h4>
              </div>
              <div className="h-80 flex items-center justify-center bg-gray-100 rounded-md overflow-hidden">
                {isProcessing ? (
                  <div className="flex flex-col items-center">
                    <Loader2 className="h-8 w-8 text-gray-400 animate-spin" />
                    <p className="mt-2 text-sm text-gray-500">Procesando imagen...</p>
                  </div>
                ) : enhancedImageUrl ? (
                  <div className="relative w-full h-full">
                    <Image
                      src={enhancedImageUrl}
                      alt="Imagen mejorada"
                      fill
                      style={{ objectFit: 'contain' }}
                    />
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">La imagen mejorada aparecerá aquí</p>
                )}
              </div>
              {metadata && (
                <div className="mt-2 text-xs text-gray-500">
                  {metadata.processed_size && (
                    <p>Dimensiones: {metadata.processed_size[1]}x{metadata.processed_size[0]} px</p>
                  )}
                  <p>Factor de escala: {metadata.scale_factor}x</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
