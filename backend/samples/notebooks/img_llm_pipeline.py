# tested in python >= 3.12, < 3.13, use main pyproject.toml
import os
import sys

project_root = os.path.abspath(os.path.join(os.getcwd(), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports and setup
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pprint
import json
import random
from lib.image.llm_pipeline import optimize_pipeline, build_pipeline, process_image

# Ollama client
from ollama import chat

# Define LLM models to test
models = [
    "llama3.2-vision:11b",
    "deepseek-r1:8b",
    "deepseek-r1:32b"
]

param_space = {
    "denoise": {"h": [5, 10, 15], "template_window": [3, 7]},
    "contrast": {"alpha": [1.0, 1.2, 1.5], "beta": [0, 10, 20]},
    "resize": {"width": [800, 1024, 1280]},
    "normalize": {"clipLimit": [1.0, 2.0], "tileGrid": [(8, 8)]},
    "crop": {"margin": [0, 5, 10]},
    "hash": {}
}

def generate_random_config():
    return {
        "use": {
            "rotate": random.choice([True, False]),
            "denoise": True,
            "contrast": random.choice([True, False]),
            "resize": True,
            "normalize": True,
            "crop": random.choice([True, False]),
            "hash": True
        },
        "params": {
            "denoise": {"h": 10, "template_window": 7},
            "contrast": {"alpha": 1.2, "beta": 10},
            "resize": {"width": 1024},
            "normalize": {"clipLimit": 2.0, "tileGrid": (8, 8)},
            "crop": {"margin": 5}
        }
    }



prompt = f"""
  An image was processed and the following metrics were evaluated:

  - Blur reduction: {data['metrics']['blur_reduction']:.2f}
  - OCR gain: {data['metrics']['ocr_gain']}
  - Overall score: {data['metrics']['score']:.2f}

  These were the initial parameters used:
  {json.dumps(data['params'], indent=2)}

  Decide which steps should be enabled based on the state of the processed image and its visual quality.
  Respond only with JSON format as in the following example:

  {{
    "use": {{
      "rotate": false,
      "denoise": true,
      "contrast": true,
      "resize": true,
      "normalize": true,
      "crop": false,
      "hash": true
    }},
    "params": {{
      "denoise": {{ "h": 10, "template_window": 7 }},
      "contrast": {{ "alpha": 1.2, "beta": 10 }},
      "resize": {{ "width": 1024 }},
      "normalize": {{ "clipLimit": 2.0, "tileGrid": [8, 8] }},
      "crop": {{ "margin": 5 }}
    }}
  }}
"""


def llm_adjust_callback(data, model_name="llama3.2:3b", custom_prompt):
    response = chat(
        model=model_name,
        messages=[{"role": "user", "content": custom_prompt}]
    )
    try:
        parsed = json.loads(response['message']['content'])
    except Exception as e:
        
        parsed = generate_random_config()
    return parsed

def evaluate_image_quality(orig, proc):
    b_orig = cv2.Laplacian(cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    b_proc = cv2.Laplacian(cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    text_orig = len(pytesseract.image_to_string(orig))
    text_proc = len(pytesseract.image_to_string(proc))
    return {
        'blur_reduction': b_proc - b_orig,
        'ocr_gain': text_proc - text_orig,
        'score': (b_proc - b_orig) + (text_proc - text_orig)
    }

def optimize_pipeline(orig_image, param_space, llm_call, max_iter=3):
    best = {'score': -float('inf')}
    for _ in range(max_iter):
        current_params = {k: {sk: random.choice(v) for sk, v in sp.items()} for k, sp in param_space.items()}
        config = {
            "use": {k: True for k in ["rotate", "denoise", "contrast", "resize", "normalize", "crop", "hash"]},
            "params": current_params
        }
        steps = build_pipeline(config)
        img, _ = process_image(orig_image, steps)
        metrics = evaluate_image_quality(orig_image, img)

        new_config = llm_call({
            "orig": orig_image,
            "proc": img,
            "metrics": metrics,
            "params": current_params
        })
        new_steps = build_pipeline(new_config)
        new_img, history = process_image(orig_image, new_steps)
        new_metrics = evaluate_image_quality(orig_image, new_img)

        if new_metrics['score'] > best['score']:
            best.update({
                'image': new_img,
                'config': new_config,
                'metrics': new_metrics,
                'history': history,
                'score': new_metrics['score']
            })
    return best


best_result = optimize_pipeline(orig, param_space, llm_adjust_callback)

print("Mejor configuración:")
print(json.dumps(best_result['config'], indent=2))
print("Métricas:")
print(best_result['metrics'])

# Visualizar resultado
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB))
plt.title("Original")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(best_result['image'], cv2.COLOR_BGR2RGB))
plt.title("Optimizada por LLM")
plt.axis("off")
plt.show()

# Mostrar historial de pasos aplicados
for entry in best_result['history']:
    print(entry)

