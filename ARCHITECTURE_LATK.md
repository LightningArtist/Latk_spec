# Lightning Artist Toolkit (Latk) Format & Architecture Guide

This document provides a comprehensive specification and implementation guide for the **Lightning Artist Toolkit (Latk)** 3D brushstroke file format. It is optimized for AI agents interacting with Latk files across various programming languages.

## 1. Overview 
Latk refers to the Lightning Artist Toolkit. It serves as a universal, open-source data format and pipeline designed specifically for volumetric 3D vector drawing and stroke-based animation.

The toolkit addresses the fragmentation of 3D stroke data by providing a standardized way to read, write, and manipulate spatial drawings across different software environments.

### 1.1. The Latk JSON Specification
The core of the Lightning Artist Toolkit is its structured JSON format, which organizes animation data into a strict hierarchy that is easily parsed and mathematically manipulated:

- Layers: The top-level container, allowing multiple discrete visual elements to exist within the same file.

- Frames: Sequential temporal containers within each layer.

- Strokes: Individual continuous lines drawn by the user within a specific frame.

- Points: The foundational data units making up each stroke. Each point contains x, y, and z spatial coordinates, along with metadata such as RGBA color values, pressure, and brush radius.

### 1.2. Primary Applications
Because Latk reduces complex volumetric animations down to raw mathematical coordinates in a structured JSON schema, it is heavily utilized in advanced computational workflows:

#### 1.2.1. Cross-Platform Interchange
Moving spatial drawings seamlessly between creation tools (like Tilt Brush or Quill) and rendering/programming environments (such as Blender, TouchDesigner, openFrameworks, Unity, and p5.js). The most immediate use of Latk is bridging disparate creative ecosystems that otherwise cannot communicate. It acts as a universal translator for spatial data.

- VR to Traditional 3D Pipelines: An artist sketches a dynamic, volumetric scene in a VR application like Tilt Brush. Exporting this as a .latk JSON file allows the animation to be imported directly into Blender. A Python script parses the Latk layers and frames, converting the raw x, y, z point data into native Grease Pencil strokes or Bezier curves. This allows a hand-drawn spatial sketch to inherit complex studio lighting, camera tracking, and rendering engines.

- Asset Portability for Live Visuals: That exact same .latk file can be dropped into TouchDesigner or Isadora without conversion. In a live performance, the stroke paths can be assigned to particle emitters, allowing real-time audio reactivity to drive the thickness or color of the strokes as a DJ performs, completely bypassing traditional static video rendering.

#### 1.2.2. Programmatic Manipulation
Allowing developers to apply mathematical transformations, noise fields, or procedural generation directly to the stroke data before rendering.

Because Latk breaks down art into pure mathematical arrays, developers can apply generative and procedural transformations to hand-drawn assets in real time.

- Algorithmic Distortion: A 3D character is animated by hand, but the developer wants the character to look like it is underwater or glitching. Using a framework like openFrameworks (C++) or p5.js, a script parses the Latk JSON and applies 3D Perlin noise or sine wave displacements to specific point coordinates on every frame at runtime. The original hand-drawn data remains untouched, but the rendered output dynamically shifts and warps.

- Procedural Instancing: Instead of animating a flock of birds, an artist animates a single bird cycle in Latk. A creative coding environment reads that single JSON object and algorithmically duplicates it 500 times, applying slight matrix offsets (translation, rotation, scale, and frame-delay) to each instance. A single asset becomes a complex, swirling 3D particle system driven by code.

#### 1.2.3. Machine Learning Integration
Serving as a clean, standardized dataset format for training AI models on stroke-based animation, enabling gesture recognition, style transfer, or the generative synthesis of new 3D motion paths.

Standard video pixels are noisy and inefficient for training AI on the mechanics of human motion and drawing. Latk provides clean, structured vector data, making it highly valuable for deep learning architectures.

#### 1.2.4. Generative Stroke Prediction
Because Latk data is sequential (Points → Strokes → Frames), it is an ideal format for training recurrent neural networks or transformer models in PyTorch. An AI model trained on thousands of Latk files can learn the kinematic velocity and trajectory of human drawing, enabling the system to auto-complete an artist's stroke or generate infinite in-between frames for a 12-fps hand-drawn animation.

Instead of trying to predict the color of the next pixel in a video, this approach predicts the next spatial coordinate (x, y, z) and state (pressure, brush size) of a human's hand.

- How it works: Because a Latk file represents a sequence of points over time, the data can be fed directly into Recurrent Neural Networks (RNNs) or Transformer models. The AI learns the kinematic velocity, trajectory, and structure of how humans draw in 3D space.

- Existing Examples (Analogous): The foundational example of this concept is Google's SketchRNN, which uses a sequence-to-sequence variational autoencoder to predict and auto-complete 2D vector strokes. By mapping Latk's structured 3D point data into similar architectures using PyTorch, developers can build models that autocomplete a volumetric sketch, smoothly interpolate missing "in-between" frames for a 12-fps VR animation, or convert 3D markerless motion capture (like MediaPipe skeleton data) directly into stylized vector strokes.   

#### 1.2.5. Spatial Conditioning for Diffusion Models
Latk's raw skeletal and contour data can be extracted to guide latent space generation. In complex image-to-video pipelines, the 3D stroke data from a Latk file can be rendered out as depth maps, lineart, or pose estimations to serve as precise structural conditioning for tools like ControlNet within ComfyUI. Diffusion models are notoriously volatile when generating video because they struggle with temporal consistency; this anchors the volatile outputs of diffusion models, enforcing temporal consistency in stylized AI video generation. Latk provides the explicit 3D geometry needed to lock the model in place.

- How it works: A 3D animation created in Latk is rendered out not as a finished image, but as structural data—such as a dense depth map, a clean lineart pass, or a rigid skeletal pose. This data is then used as a highly precise guide layer for an AI generation pipeline, ensuring the final rendered output adheres strictly to the original hand-drawn volume.

- Existing Examples: This is heavily utilized in node-based workflows like ComfyUI. A user might take a rough 3D volumetric animation from Latk, extract its structural maps, and feed those directly into ControlNet (using Depth or OpenPose models) alongside an animation module like AnimateDiff. The diffusion model applies complex textures, lighting, and style (e.g., turning a rough stick figure into a hyper-realistic robot), but the ControlNet uses the Latk-derived data to anchor the generation. Because the underlying Latk data is mathematically continuous in 3D space, it eliminates the flickering and warping that typically plagues AI video generation.



## 2. Latk JSON Format Specification

The Latk format represents 3D spatial drawings and volumetric animations over time. The JSON structure is hierarchical, heavily inspired by Blender's Grease Pencil.

### 2.1. JSON Structure
```json
{
    "creator": "latk.py",
    "version": 2.9,
    "grease_pencil": [
        {
            "layers": [
                {
                    "name": "GP_Layer",
                    "frames": [
                        {
                            "strokes": [
                                {
                                    "color": [ 0.20259166, 0.032980658, 0.9169371, 1.0 ],
                                    "fill_color": [ 0.0, 0.0, 0.0, 1.0 ],
                                    "brush_name": "optional",
                                    "brush_creator": "optional",
                                    "points": [
                                        {
                                            "co": [ 1.1935601, 0.98816276, -0.74828625 ], 
                                            "pressure": 0.50230646, 
                                            "strength": 0.50914043, 
                                            "vertex_color": [ 0.0, 0.0, 0.0, 1.0 ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

#### 2.1.1. Spec Hierarchy Details
- **Root Object**: Contains metadata (`creator`, `version`) and the main `grease_pencil` array.
- **`grease_pencil`**: Array containing animation project data.
- **`layers`**: Array of layer objects (e.g., for separating colors or elements).
- **`frames`**: Array of frames within a layer, representing a snapshot in time.
- **`strokes`**: A continuous line drawn by the user. Includes RGBA arrays for `color` and `fill_color`.
- **`points`**: Array of vertices. `co` is a 3D coordinate `[x, y, z]`. Also stores `pressure`, `strength`, and `vertex_color`.

---

#### 2.1.2. Universal Core Data Model
Across all language implementations, Latk libraries follow a standard Object-Oriented hierarchy:

- **`Latk`**: The root container. Manages the animation timeline, file I/O (reads/writes `.json` and zipped `.latk` formats), and holds a list of `LatkLayer`s.
- **`LatkLayer`**: Represents a single layer. Contains a sequence of `LatkFrame`s and tracks the `currentFrame`.
- **`LatkFrame`**: Represents a single frame of animation in a timeline sequence. Contains a list of `LatkStroke` instances.
- **`LatkStroke`**: The atomic visual element representing a continuous 3D line. Contains a list of `LatkPoint` instances and styling properties (color/size). Usually provides methods for stroke modification (smoothing, splitting, refining, cleaning).
- **`LatkPoint`**: The fundamental vertex unit. Holds the 3D coordinate (`co`/`PVector`/`ofVec3f`), pressure, strength, and color.

---

### 2.2. Language Implementations

#### 2.2.1. Python (`latkpy`)
- **Use Case:** Headless processing, geometric optimization, scripting.
- **File I/O:** Supports standard `.json` and `.latk` zipped operations via `InMemoryZip` (`latk_zip.py`). Also parses Google Tilt Brush (`.tilt`) files (`latk_tilt.py`).
- **Geometry Processing:**
  - `latk_rdp.py`: Ramer-Douglas-Peucker algorithm for stroke simplification.
  - `latk_kmeans.py`: K-means clustering for spatial optimization and color quantization.

#### 2.2.2. C++ / openFrameworks (`ofxLatk`)
- **Use Case:** High-performance rendering, native desktop/embedded applications.
- **Dependencies:** Bundled with `JsonCpp` and a lightweight `zip` library (no external Poco dependency).
- **Execution Flow:** `Latk::run()` checks elapsed time against framerate (`checkInterval()`), increments `currentFrame` on `LatkLayer`s, and tells strokes to update.
- **Rendering:** Applications access the active `LatkStroke` points to draw paths or meshes.

#### 2.2.3. JavaScript (`latk.js`)
- **Use Case:** Web environments (Three.js, p5.js, 2D Canvas).
- **Dependencies:** Bundled with `JSZip` for unzipping `.latk`, `.sketch` (Tilt Brush), and Oculus Quill archives.
- **Processing Utilities:** Includes methods like `clean(epsilon)` (RDP simplification), `normalize()`, `refine()`, `smoothStroke()`, and `splitStroke()`.

#### 2.2.4. Java / Processing (`latkProcessing`)
- **Use Case:** Creative coding in the Processing IDE.
- **Data Flow:** Integrates directly into the Processing `draw()` loop. Calling `latk.run()` cascades down the hierarchy to render internally cached `PShape` objects at the stroke level.
- **Importers:** Contains `TiltLoader` and `QuillLoader` for converting binary formats into the native Latk structure.

#### 2.2.5. C# / Unity (`latkUnity`)
- **Use Case:** Real-time game engines, VR/AR, Unity projects.
- **Architecture:** Driven by a central `LightningArtist.cs` MonoBehaviour.
- **Rendering System:** Abstracted via `LatkStrokeRenderer`. The default is `LatkLineRenderer` (uses Unity's `LineRenderer`), allowing developers to implement custom shaders, ribbon meshes, or particles easily.
- **Modules:** Segregated into `Importers` (Tilt/Quill), `Drawing` (primitives generation), `Input` (keyboard, mouse, VR controllers), and `Playback` (syncing with Unity's Animator/Audio/Video).

---

### 2.3. Agent Guidelines for Latk Operations

When an AI agent is tasked with generating or manipulating Latk files, adhere to these rules:

- **Hierarchy Integrity:** Always respect the 5-tier nested structure (`Latk` > `Layer` > `Frame` > `Stroke` > `Point`). Skipping a level will corrupt the file.
- **File Formats:** By default, save data as flat `.json` for debugging or direct text manipulation. For production, compress the `.json` into a `.zip` and rename the extension to `.latk`. The libraries handle both automatically.
- **Point Reduction:** 3D drawing data is dense. Use RDP algorithms (`clean()` or `latk_rdp.py`) when transferring strokes to lower file sizes and improve runtime performance.
- **Coordinate Normalization:** When mixing sources (e.g., Tilt Brush with Latk), utilize the built-in `normalize()` functions to scale points into a unified 0-1 bounding box.
- **Timeline Handling:** Animations are driven by `LatkLayer`s traversing `LatkFrame` arrays. If creating a static 3D drawing (non-animated), place all `LatkStroke`s inside a single `LatkFrame` (index 0).

## 3. LatkL JSONL Specification (NAPLPS Style)

LatkL is a JSON Lines (JSONL) based streaming specification for the Latk format, inspired by the historical Telidon/NAPLPS standard. 

While the standard Latk format is a hierarchical JSON structure (`Latk` > `Layer` > `Frame` > `Stroke` > `Point`), the LatkL JSONL variant flattens the drawing process into a stream of sequential drawing instructions (opcodes). This is ideal for progressive rendering, real-time streaming, and lower-memory processing, akin to how Telidon/NAPLPS systems decoded Picture Description Instructions (PDIs).

### 3.1. JSONL Structure

Instead of loading the entire `grease_pencil` array into memory, a LatkL JSONL file consists of one JSON object per line. Each object contains an `op` (opcode) field that instructs the renderer on what action to take next, establishing state (like current layer, frame, or color) that persists for subsequent drawing commands. A typical sequence would look like this:

```json
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

#### 3.1.1. Header and Metadata Opcodes
Initializes the stream and sets up global parameters.

- **`header`**: Specifies the creator and version. 
  `{"op": "header", "creator": "latk.py", "version": 2.9}`

#### 3.1.2. State and Control Instruction Opcodes
Similar to NAPLPS setting up domains or current state, these commands set the current layer and frame for subsequent drawing operations.

- **`layer`**: Sets the active layer.  
  `{"op": "layer", "name": "GP_Layer"}`
- **`frame`**: Sets the active frame index within the current layer.  
  `{"op": "frame", "index": 0}`
- **`color`**: Sets the active stroke and fill colors. These colors will apply to subsequent strokes unless overridden.
  `{"op": "color", "stroke": [0.2025, 0.0329, 0.9169, 1.0], "fill": [0.0, 0.0, 0.0, 1.0]}`
- **`brush`**: Sets brush attributes.
  `{"op": "brush", "name": "optional", "creator": "optional"}`

#### 3.1.3. Drawing Instruction Opcodes
Analogous to NAPLPS lines, polygons, and arcs, these commands define the actual 3D brushstrokes. Since strokes can contain many points, we define commands to begin, build, and end a stroke.

- **`stroke_start`**: Begins a new continuous line using the current color and brush state.
  `{"op": "stroke_start"}`
- **`point`**: Adds a vertex to the current active stroke.
  `{"op": "point", "co": [1.1935, 0.9881, -0.7482], "pressure": 0.5023, "strength": 0.5091, "vertex_color": [0.0, 0.0, 0.0, 1.0]}`
- **`stroke_end`**: Completes the current continuous line.
  `{"op": "stroke_end"}`

For a slightly less granular approach that reduces file size overhead but still streams stroke by stroke.

- **`stroke`**: Defines an entire stroke and all its points in a single line. This can include stroke-specific colors and brush metadata as optional overrides.
  `{"op": "stroke", "points": [{"co": [1, 2, 3], "pressure": 1.0}, ...]}`

### 3.2. Benefits of the LatkL JSONL Approach
- **Progressive Rendering:** Like historical Telidon terminals, viewers can draw the 3D scene step-by-step as data arrives over a network connection.
- **Infinite Streams:** Suitable for real-time multiplayer VR drawing or live performances where the stream never officially "ends" and the document does not need a closing bracket.
- **Memory Efficiency:** Eliminates the need to parse massive monolithic JSON structures into memory all at once, allowing even embedded devices to process dense 3D drawings line by line.
