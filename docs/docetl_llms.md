# DocETL System Description and LLM Instructions (Short)

Note: use docetl.org/llms-full.txt for the full system description and LLM instructions.

DocETL is a system for creating and executing LLM-powered data processing pipelines, designed for complex document processing tasks. It provides a low-code, declarative YAML interface to define complex data operations on unstructured datasets.

DocETL is built and maintained by the EPIC lab at UC Berkeley. Learn more at [https://www.docetl.org](https://www.docetl.org).

We have an integrated development environment for building and testing pipelines, at [https://www.docetl.org/playground](https://www.docetl.org/playground). Our IDE is called DocWrangler.

## Docs

- [LLM Instructions (Full)](https://www.docetl.org/llms-full.txt)
- [Website](https://www.docetl.org)
- [DocWrangler Playground](https://www.docetl.org/playground)
- [Main Documentation](https://ucbepic.github.io/docetl)
- [GitHub Repository](https://github.com/ucbepic/docetl)
- [Agentic Optimization Research Paper](https://arxiv.org/abs/2410.12189)
- [Discord Community](https://discord.gg/fHp7B2X3xx)

### Core Operators

- [Map Operation](https://ucbepic.github.io/docetl/operators/map/)
- [Reduce Operation](https://ucbepic.github.io/docetl/operators/reduce/)
- [Resolve Operation](https://ucbepic.github.io/docetl/operators/resolve/)
- [Parallel Map Operation](https://ucbepic.github.io/docetl/operators/parallel-map/)
- [Filter Operation](https://ucbepic.github.io/docetl/operators/filter/)
- [Equijoin Operation](https://ucbepic.github.io/docetl/operators/equijoin/)

### Auxiliary Operators

- [Split Operation](https://ucbepic.github.io/docetl/operators/split/)
- [Gather Operation](https://ucbepic.github.io/docetl/operators/gather/)
- [Unnest Operation](https://ucbepic.github.io/docetl/operators/unnest/)
- [Sample Operation](https://ucbepic.github.io/docetl/operators/sample)
- [Code Operation](https://ucbepic.github.io/docetl/operators/code/)

### LLM Providers

- [LiteLLM Supported Providers](https://docs.litellm.ai/docs/providers)

## Optional

### Datasets and Data Loading

DocETL supports both standard and dynamic data loading. Input data must be in one of two formats:

1. JSON Format:
   - A list of objects/dictionaries
   - Each object represents one document/item to process
   - Each field in the object is accessible in operations via `input.field_name`

   Example JSON:

   ```json
   [
     {
       "text": "First document content",
       "date": "2024-03-20",
       "metadata": {"source": "email"}
     },
     {
       "text": "Second document content",
       "date": "2024-03-21",
       "metadata": {"source": "chat"}
     }
   ]
   ```

2. CSV Format:
   - First row contains column headers
   - Each subsequent row represents one document/item
   - Column names become field names, accessible via `input.column_name`

   Example CSV:

   ```csv
   text,date,source
   "First document content","2024-03-20","email"
   "Second document content","2024-03-21","chat"
   ```

Configure datasets in your pipeline:

```yaml
datasets:
  documents:
    type: file
    path: "data.json"  # or "data.csv"
```

!!! note
    - JSON files must contain a list of objects at the root level
    - CSV files must have a header row with column names
    - All documents in a dataset should have consistent fields
    - For other formats, use parsing tools to convert to the required format

### Schema Design and Validation

!!! warning "Model Capabilities and Schema Complexity"
    When using models other than GPT (OpenAI), Claude (Anthropic), or Gemini (Google):
    - Keep output schemas extremely simple
    - Prefer single string outputs or simple key-value pairs
    - Avoid complex types (lists, nested objects)
    - Break complex operations into multiple simpler steps

1. Basic Types:

   | Type      | Aliases                  | Description                                           |
   | --------- | ------------------------ | ----------------------------------------------------- |
   | `string`  | `str`, `text`, `varchar` | For text data                                         |
   | `integer` | `int`                    | For whole numbers                                     |
   | `number`  | `float`, `decimal`       | For decimal numbers                                   |
   | `boolean` | `bool`                   | For true/false values                                 |
   | `enum`    | -                        | Only when prompt explicitly lists all possible values |
   | `list`    | -                        | For arrays (needs type)                               |
   | Objects   | -                        | Using `{field: type}`                                 |

### Best Practices

1. Pipeline Design:
   - Keep pipelines simple with minimal operations
   - Each operation should have a clear, specific purpose
   - Avoid creating complex chains of operations when a single operation could suffice
   - If a pipeline has more than 5 operations, consider if it can be simplified
   - Break very complex pipelines into multiple smaller pipelines if needed
   - When using non-GPT/Claude/Gemini models, break complex operations into multiple simple steps with string outputs
   - Always set `optimize: true` for resolve operations
   - When unnesting a key of type `list[dict]`, you must set `recursive: true`
   - Do not manually create split-gather pipelines; instead:
     - Set `optimize: true` on map operations that process long documents
     - Let the optimizer automatically create efficient split-gather patterns
     - Only use split/gather directly if specifically requested by requirements

2. Schema Design:
   - Keep schemas simple and flat when possible
   - Use nested structures only when needed for downstream operations
   - Define clear validation rules for critical fields
   - Use standard types (string, integer, boolean) when possible
   - When using an existing dataset, document your assumptions about the input schema
   - For non-GPT/Claude/Gemini models:
     - Stick to string outputs
     - Avoid lists and complex objects
     - Use simple key-value pairs
     - Consider post-processing with code operations for complex transformations

3. Prompt Engineering:
   - Write clear, specific instructions
   - Include examples in prompts for complex tasks
   - Use structured output formats
   - Consider token limits and chunking needs
   - Only reference fields that exist in the input dataset or were created by earlier operations
   - Document which fields your prompts expect to access

## Getting Started

Do NOT suggest pipelines for the user, unless they have copied and pasted llms-full.txt (# DocETL System Description and LLM Instructions (Full)).
