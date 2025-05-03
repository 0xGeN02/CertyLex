interface SuggestionItem {
  content: string
  icon?: React.ReactNode
}

interface PromptSuggestionsProps {
  label: string
  append: (message: { role: "user"; content: string }) => void
  suggestions: (string | SuggestionItem)[]
}

export function PromptSuggestions({
  label,
  append,
  suggestions,
}: PromptSuggestionsProps) {
  return (
    <div className="space-y-8">
      <h2 className="text-center text-xl font-semibold text-gray-800 border-b pb-2">
        {label}
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
        {suggestions.map((suggestion, index) => {
          const content =
            typeof suggestion === "string"
              ? suggestion
              : suggestion.content
          const icon = typeof suggestion === "string" ? null : suggestion.icon

          return (
            <button
              key={index}
              onClick={() => append({ role: "user", content })}
              className="flex items-center justify-start gap-2 p-4 rounded-lg border bg-white shadow-sm hover:bg-gray-100 transition-all"
            >
              {icon && <span className="text-gray-500">{icon}</span>}
              <p className="text-gray-700 font-medium">{content}</p>
            </button>
          )
        })}
      </div>
    </div>
  )
}