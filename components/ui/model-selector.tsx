import React, { useState } from 'react';
import { toast } from 'sonner';
import { ChevronDown } from 'lucide-react';

export type Model = {
  name: string;
  size: string;
  modifiedAt: string;
  modelFamily: string;
  suitableFor: string[];
};

type Props = {
  models: Model[];
  selected: string;
  onSelect: (model: string) => void;
};

export function ModelSelector({ models, selected, onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const [current, setCurrent] = useState(selected);

  const apply = () => {
    onSelect(current);
    setOpen(false);
    toast.info(`Modelo seleccionado: ${current}`, {
      description: 'El modelo ha sido cambiado.',
      duration: 2000,
    });
  };

  return (
    <>
      <button
        className="flex items-center gap-2 px-4 py-2 bg-[#9e2a2b] text-white rounded hover:bg-[#801f20] transition-colors shadow-sm border border-[#801f20]"
        onClick={() => setOpen(true)}
      >
        <span className="font-medium">Modelo: {selected}</span>
        <ChevronDown size={16} />
      </button>

      {open && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 shadow-xl border-2 border-[#9e2a2b]">
            <h3 className="text-lg font-semibold mb-4 text-[#9e2a2b] border-b pb-2">Selección de Modelo</h3>
            <ul className="space-y-2 max-h-64 overflow-auto p-2">
              {models.map((m) => (
                <li key={m.name} className="hover:bg-gray-50 rounded p-1">
                  <label className="flex items-center space-x-2 cursor-pointer w-full">
                    <input
                      type="radio"
                      name="model"
                      value={m.name}
                      checked={current === m.name}
                      onChange={() => setCurrent(m.name)}
                      className="text-[#9e2a2b] focus:ring-[#9e2a2b]"
                    />
                    <div>
                      <span className="font-medium">{m.name}</span>
                      <span className="text-sm text-gray-500 ml-2">({m.size})</span>
                    </div>
                  </label>
                </li>
              ))}
            </ul>
            <div className="mt-4 flex justify-end space-x-2 pt-2 border-t">
              <button
                className="px-3 py-1.5 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
                onClick={() => setOpen(false)}
              >
                Cancelar
              </button>
              <button
                className="px-3 py-1.5 bg-[#9e2a2b] text-white rounded hover:bg-[#801f20] transition-colors"
                onClick={apply}
              >
                Seleccionar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}