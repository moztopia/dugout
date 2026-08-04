# Barrel Generator

`barrel` is a powerful, configuration-driven tool designed to automate the creation of "barrel files" (index files that export other files) across multiple programming languages. It simplifies imports and helps maintain clean project structures.

## Core Features

- **Multi-Language Support**: Driven by `barrel.languages.yaml`, supporting Dart, TypeScript, JavaScript, and PHP out of the box.
- **Smart Exports**: Automatically handles language-specific conventions, such as stripping `.ts` and `.js` extensions from export paths.
- **Recursive Generation**: Bubbles up exports from sub-directories into parent barrels.
- **Idempotent Cleanup**: Automatically identifies and removes old generated barrels before recreation using a unique label.
- **Flexible Naming**: Depth-based naming rules (`auto`, `named`, `skip`) allow for granular control over the directory tree.
- **Deterministic**: Exports are sorted alphabetically to ensure consistent output and minimize merge conflicts.

---

## Installation & Usage

The tool is typically invoked via a shim provided in the `toolz` suite:

```bash
# Run in the directory containing barrel.yaml
barrel

# Or specify a path to a configuration file
barrel path/to/project/barrel.yaml
```

---

## Configuration (`barrel.yaml`)

Each project root must contain a `barrel.yaml` file to define the generation rules.

### Core Properties

| Property | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `language` | `string` | The target language (defined in `barrel.languages.yaml`). | `dart` |
| `filename` | `string` | The name of the top-level barrel file. | *Required* |
| `label` | `string` | A unique string on the first line to identify generated files. | *Required* |
| `prefix` | `string` | Prefix for automatically named sub-barrels. | `barrel_` |
| `exclude` | `string[]` | List of directory names to skip during traversal. | `[]` |
| `naming` | `map` | Depth-based naming rules (see below). | `{}` |

### Naming Rules

Rules are defined by directory depth (1-indexed, where 1 is the root):

- **`auto`**: Uses the folder name prefixed with the `prefix` (e.g., `_models.dart`).
- **`named`**: Uses the exact folder name (e.g., `models.dart`).
- **`skip`**: Does not create a barrel in this folder, but recurses into children.

### Example

```yaml
language: "typescript"
filename: "index.ts"
label: "// @generated - barrel"
prefix: "_"
exclude:
  - "node_modules"
  - "tests"
naming:
  2: "named"
  3: "skip"
  "N": "auto" # Default for all other depths
```

---

## Language Specifications (`barrel.languages.yaml`)

The tool's behavior is extended via `barrel.languages.yaml`. This file defines how each language handles extensions and export templates.

### Example Definition

```yaml
typescript:
  extension: ".ts"
  ignore:
    - ".spec.ts"
    - ".test.ts"
  template: 'export * from "./{path}";'
```

- **Extension Stripping**: For `typescript` and `javascript`, the tool automatically strips the extension from the `{path}` in the template, adhering to modern ESM standards.
- **Ignore Patterns**: Files matching the `ignore` list (e.g., `.g.dart` or `.spec.ts`) are excluded from exports.

---

## Technical Workflow

1. **Initialization**: Resolves the root directory based on the `barrel.yaml` location.
2. **Cleanup**: Recursively scans the tree and deletes any file whose first line exactly matches the `label`.
3. **Traversal**:
   - Scans local files (respecting `ignore` patterns).
   - Recurses into child directories (respecting `exclude` list).
4. **Bubbling**: Sub-directory barrels are exported by their parent barrels.
5. **Writing**: Sorted exports are written to the target barrel files with the identification `label`.
