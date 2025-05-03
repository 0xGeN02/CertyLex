import React from "react";

export type Hyperparameters = {
  temperature: number;
  top_p: number;
  max_tokens: number;
};

export type HyperparameterFormProps = {
  values: Hyperparameters;
  onChange: (values: Hyperparameters) => void;
};

export function HyperparameterForm({ values, onChange }: HyperparameterFormProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onChange({ ...values, [name]: parseFloat(value) });
  };

  return (
    <div className="border rounded-md p-4 mb-4 w-full">
      <h2 className="font-semibold mb-2">Ajustar Hiperparámetros</h2>
      <div className="flex flex-col gap-2">
        <label>
          Temperature
          <input
            type="number"
            name="temperature"
            min="0"
            max="2"
            step="0.01"
            value={values.temperature}
            onChange={handleChange}
            className="ml-2 border rounded px-2 py-1 w-24"
          />
        </label>
        <label>
          Top-p
          <input
            type="number"
            name="top_p"
            min="0"
            max="1"
            step="0.01"
            value={values.top_p}
            onChange={handleChange}
            className="ml-2 border rounded px-2 py-1 w-24"
          />
        </label>
        <label>
          Max tokens
          <input
            type="number"
            name="max_tokens"
            min="1"
            max="4096"
            step="1"
            value={values.max_tokens}
            onChange={handleChange}
            className="ml-2 border rounded px-2 py-1 w-24"
          />
        </label>
      </div>
    </div>
  );
}
