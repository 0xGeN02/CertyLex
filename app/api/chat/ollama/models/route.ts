import { NextResponse } from 'next/server';

const OLLAMA_BASE_URL = process.env.OLLAMA_HOST || 'http://localhost:11434';

interface OllamaModel {
    name: string;
    tag: string;
    size: number;
    modified_at: string;
}

interface OllamaResponse {
    models: OllamaModel[];
}

export async function GET() {
    try {
        const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            return NextResponse.json(
                { error: 'Failed to fetch models from Ollama' }, 
                { status: 500 }
            );
        }

        const data: OllamaResponse = await response.json();
        
        // Format the data into a more usable structure
        const formattedModels = data.models.map((model) => ({
            name: model.name,
            tag: model.tag,
            size: model.size,
            modifiedAt: model.modified_at,
            modelFamily: getModelFamily(model.name),
            suitableFor: getModelCapabilities(model.name)
        }));

        return NextResponse.json({ models: formattedModels });
    } catch (error) {
        console.error('Error fetching models:', error);
        return NextResponse.json({ error: 'Failed to fetch models' }, { status: 500 });
    }
}

// Helper function to categorize models by family
function getModelFamily(modelName: string): string {
    const name = modelName.toLowerCase();
    if (name.includes('llama')) return 'Llama';
    if (name.includes('-vision')) return 'Llama-Vision';
    if (name.includes('mistral')) return 'Mistral';
    if (name.includes('phi')) return 'Phi';
    if (name.includes('gemma')) return 'Gemma';
    if (name.includes('codellama')) return 'CodeLlama';
    if (name.includes('orca')) return 'Orca';
    return 'Other';
}

// Helper function to suggest use cases
function getModelCapabilities(modelName: string): string[] {
    const capabilities = [];
    const name = modelName.toLowerCase();
    
    if (name.includes('code') || name.includes('starcoder') || name.includes('codellama')) {
        capabilities.push('Code Generation', 'Technical Documentation');
    }
    
    if (name.includes('3b') || name.includes('8b')) {
        capabilities.push('Quick Responses', 'Lower Resource Usage');
    }
    
    if (name.includes('11b') || name.includes('14b')) {
        capabilities.push('Balanced Performance', 'General Tasks');
    }
    
    if (name.includes('32b') || name.includes('70b') || name.includes('40b')) {
        capabilities.push('Complex Reasoning', 'High Quality Responses');
    }
    
    if (capabilities.length === 0) {
        capabilities.push('General Purpose');
    }
    
    return capabilities;
}