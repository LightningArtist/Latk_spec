# Latk JSONL Specification (Telidon/NAPLPS Style)

This document proposes a new JSON Lines (JSONL) based streaming specification for the Latk format, inspired by the historical Telidon / NAPLPS standard. 

While the standard Latk format is a hierarchical JSON structure (`Latk` > `Layer` > `Frame` > `Stroke` > `Point`), this JSONL variant flattens the drawing process into a stream of sequential drawing instructions (opcodes). This is ideal for progressive rendering, real-time streaming, and lower-memory processing, akin to how Telidon decoded Picture Description Instructions (PDIs).

## Architecture

Instead of loading the entire `grease_pencil` array into memory, a Latk JSONL file consists of one JSON object per line. Each object contains an `op` (opcode) field that instructs the renderer on what action to take next, establishing state (like current layer, frame, or color) that persists for subsequent drawing commands.

### Opcodes

#### 1. Header & Metadata
Initializes the stream and sets up global parameters.
* **`header`**: Specifies the creator and version.
  ```json
  {"op": "header", "creator": "latk.py", "version": 2.9}
  ```

#### 2. State & Control Instructions
Similar to NAPLPS setting up domains or current state, these commands set the current layer and frame for subsequent drawing operations.
* **`layer`**: Sets the active layer.
  ```json
  {"op": "layer", "name": "GP_Layer"}
  ```
* **`frame`**: Sets the active frame index within the current layer.
  ```json
  {"op": "frame", "index": 0}
  ```
* **`color`**: Sets the active stroke and fill colors. These colors will apply to subsequent strokes unless overridden.
  ```json
  {"op": "color", "stroke": [0.2025, 0.0329, 0.9169, 1.0], "fill": [0.0, 0.0, 0.0, 1.0]}
  ```
* **`brush`**: Sets brush attributes.
  ```json
  {"op": "brush", "name": "optional", "creator": "optional"}
  ```

#### 3. Drawing Instructions (Primitives)
Analogous to NAPLPS lines, polygons, and arcs, these commands define the actual 3D brushstrokes. Since strokes can contain many points, we define commands to begin, build, and end a stroke.
* **`stroke_start`**: Begins a new continuous line using the current color and brush state.
  ```json
  {"op": "stroke_start"}
  ```
* **`point`**: Adds a vertex to the current active stroke.
  ```json
  {"op": "point", "co": [1.1935, 0.9881, -0.7482], "pressure": 0.5023, "strength": 0.5091, "vertex_color": [0.0, 0.0, 0.0, 1.0]}
  ```
* **`stroke_end`**: Completes the current continuous line.
  ```json
  {"op": "stroke_end"}
  ```

#### 4. Batch Drawing (Alternative)
For a slightly less granular approach that reduces file size overhead but still streams stroke by stroke.
* **`stroke`**: Defines an entire stroke and all its points in a single line. This can include stroke-specific colors and brush metadata as optional overrides.
  ```json
  {"op": "stroke", "points": [{"co": [1, 2, 3], "pressure": 1.0}, ...]}
  ```

## Example Stream

A typical sequence would look like this:

```jsonl
{"op": "header", "creator": "latk.py", "version": 2.9}
{"op": "layer", "name": "GP_Layer"}
{"op": "frame", "index": 0}
{"op": "color", "stroke": [0.2025, 0.0329, 0.9169, 1.0], "fill": [0.0, 0.0, 0.0, 1.0]}
{"op": "brush", "name": "default", "creator": "user"}
{"op": "stroke_start"}
{"op": "point", "co": [1.1935, 0.9881, -0.7482], "pressure": 0.5023, "strength": 0.5091}
{"op": "point", "co": [1.2001, 0.9500, -0.7000], "pressure": 0.6000, "strength": 0.5091}
{"op": "stroke_end"}
```

## Benefits of the JSONL Approach
1. **Progressive Rendering:** Like historical Telidon terminals, viewers can draw the 3D scene step-by-step as data arrives over a network connection.
2. **Infinite Streams:** Suitable for real-time multiplayer VR drawing or live performances where the stream never officially "ends" and the document does not need a closing bracket.
3. **Memory Efficiency:** Eliminates the need to parse massive monolithic JSON structures into memory all at once, allowing even embedded devices to process dense 3D drawings line by line.
