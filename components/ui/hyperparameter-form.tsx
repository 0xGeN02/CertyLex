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
    <div className="space-y-4">
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-medium text-sm text-gray-700 mb-3">Model Parameters</h3>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <label htmlFor="temperature" className="text-sm font-medium text-gray-700">
                Temperature: {values.temperature}
              </label>
              <span className="text-xs text-gray-500">Creativity</span>
            </div>
            <input
              id="temperature"
              type="range"
              name="temperature"
              min="0"
              max="2"
              step="0.01"
              value={values.temperature}
              onChange={handleChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Precise</span>
              <span>Creative</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <label htmlFor="top_p" className="text-sm font-medium text-gray-700">
                Top-p: {values.top_p}
              </label>
              <span className="text-xs text-gray-500">Diversity</span>
            </div>
            <input
              id="top_p"
              type="range"
              name="top_p"
              min="0"
              max="1"
              step="0.01"
              value={values.top_p}
              onChange={handleChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <label htmlFor="max_tokens" className="text-sm font-medium text-gray-700">
                Max tokens: {values.max_tokens}
              </label>
              <span className="text-xs text-gray-500">Response length</span>
            </div>
            <input
              id="max_tokens"
              type="range"
              name="max_tokens"
              min="100"
              max="4096"
              step="100"
              value={values.max_tokens}
              onChange={handleChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
}