const modelfile = {
  // Input structure
  input: {
    language: "es", // Force Spanish input
    format: {
      question: `Por favor, responde exclusivamente en español y sigue estrictamente el siguiente formato:

                Título: [Escribe un título aquí]

                Introducción:
                [Escribe una breve introducción aquí]

                Detalles:
                [Proporciona una explicación detallada aquí]

                Conclusión:
                [Escribe una conclusión aquí]

                Pregunta: {{user_input}}`,
    },
  },

  // Output structure
  output: {
    language: "es", // Force Spanish output
    format: {
      title: "Título: {{title}}",
      introduction: "Introducción: {{introduction}}",
      details: "Detalles: {{details}}",
      conclusion: "Conclusión: {{conclusion}}",
    },
  },

  // Additional constraints
  constraints: {
    maxTokens: 500,
    temperature: 0.7,
  },
};

export default modelfile;