# Project Documentation: Choosing XML Format Over HTML

## Introduction

This project processes and trains intelligent systems using data from the BOE (Boletin Oficial del Estado). In the data ingestion pipeline, I had to choose between two available formats: XML and HTML. After careful consideration, I opted for the XML format. This README explains the rationale behind this choice with examples.

## Why XML?

### Structured Data

- **XML is designed for data interchange:**  
  XML provides a clear and well-defined structure, which allows for consistent parsing and extraction of metadata and textual content.
- **Ease of annotation:**  
  XML's customizable tags enable us to easily annotate and organize the information according to our project requirements. For example, metadata such as `<identificador>`, `<titulo>`, and `<fecha_publicacion>` are explicitly defined and nested.

### Reduced Noise

- **Minimal presentation markup:**  
  Unlike HTML, which is primarily intended for presentation (with tags like `<div>`, `<span>`, and `<link>` that add noise), XML focuses solely on content. This means less preprocessing is needed to extract pure textual data for training language models.
- **Consistency across documents:**  
  With XML, the structure remains consistent even if visual styling or layout changes over time in the original source.

## Examples

### XML Example

Below is a simplified snippet from a BOE XML document:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<documento fecha_actualizacion="20181023201505">
  <metadatos>
    <identificador>BOE-A-2014-1</identificador>
    <titulo>Orden ECD/2467/2013, de 16 de diciembre...</titulo>
    <fecha_publicacion>20140101</fecha_publicacion>
    <!-- Other metadata fields -->
  </metadatos>
  <texto>
    <p class="parrafo">La Sala de lo Contencioso Administrativo, Sección Segunda...</p>
    <!-- Additional paragraphs -->
  </texto>
</documento>
```

## Why XML for Machine Learning and NLP

XML offers a strictly structured format that streamlines the extraction and labeling of data, eliminating the presentation-based tags found in HTML. This consistency allows easier NLP preprocessing, as tokens and metadata are clearly nested. As a result, machine learning models can focus on relevant linguistic features without dealing with irrelevant layout elements, boosting overall performance and simplifying data pipelines.

## Data Processing Pipeline (Mermaid Diagram)

```mermaid
graph LR
    A[Fetch BOE Data] --> B[Parse XML]
    B --> C[Extract Relevant Sections]
    C --> D[Clean & Normalize Text]
    D --> E[Feature Engineering & Labeling]
    E --> F[Training Data Generation]
    F --> G[Model Training]
```

## Why Not Use Raw TXT?

Using plain text makes it harder to maintain structure and metadata. Parsing or annotating unstructured data becomes unpredictable, slowing down NLP tasks and complicating data segmentation.
