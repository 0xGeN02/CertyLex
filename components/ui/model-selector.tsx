import React, { useState } from 'react';

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
  };

  return (
    <>
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded"
        onClick={() => setOpen(true)}
      >
        Modelo: {selected}
      </button>

      {open && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 w-80">
            <h3 className="text-lg font-semibold mb-4">Elige un modelo</h3>
            <ul className="space-y-2 max-h-48 overflow-auto">
              {models.map((m) => (
                <li key={m.name}>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="model"
                      value={m.name}
                      checked={current === m.name}
                      onChange={() => setCurrent(m.name)}
                    />
                    <span>{m.name} ({m.size})</span>
                  </label>
                </li>
              ))}
            </ul>
            <div className="mt-4 flex justify-end space-x-2">
              <button
                className="px-3 py-1 bg-gray-200 rounded"
                onClick={() => setOpen(false)}
              >
                Cancelar
              </button>
              <button
                className="px-3 py-1 bg-blue-600 text-white rounded"
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