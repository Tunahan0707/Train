# Physics implementation audit

Audit baseline: `physics` branch, 2026-11-18.

This document distinguishes existing prototype behavior from verified engineering capability. A visible symbol, editable text field, or menu entry is not evidence that a physical model or end-to-end workflow is complete.

## Current verified-by-source-code capabilities

- PySide6 schematic editor with selection, multi-selection, placement, drag/drop, rotation, duplication, undo/redo, zoom and pan.
- Symbol definitions for resistor, capacitor, inductor, diode, LED, BJT, MOSFET, fuse, potentiometer, DC source, AC source, battery, switch, ground and wire.
- Movable orthogonal wire graphics and a geometric netlist builder. Wire endpoints, component terminals, ground references and contacts to wire segments can be grouped. A crossing without endpoint contact is not a junction.
- JSON project save/load for one named schematic scene (format v2, with v1 compatibility).
- Inline component value and instance-name editing; rename operations participate in undo/redo.
- Linear DC operating-point analysis using modified nodal analysis for resistors, ideal DC voltage sources, batteries, ideal closed switches, ideal capacitors (open circuit) and ideal inductors (zero-volt branch).
- Engineering suffix parsing and Gaussian elimination unit tests.
- Clipboard copy/paste and duplicate operations are present in the workspace code.

## Important limitations found

### Electrical models
- Most component symbols are not backed by electrical equations.
- The current DC solver does not model capacitor/inductor transient response, AC sources, diodes, LEDs, BJTs, MOSFETs, fuses or potentiometers.
- It has no component tolerance, voltage/current/power ratings, thermal model, internal resistance, current limiting, battery state, or failure model.
- It has no time-domain integrator, nonlinear Newton iteration, convergence controls, or event handling.
- A solver result must never be shown as a complete circuit result when unsupported devices are present. The DC solver was changed to reject unsupported devices rather than silently omit them.

### Connectivity and editing
- Wires can now be selected and moved as whole objects, but their endpoints and bends cannot yet be edited interactively; there is no terminal-to-terminal wire drawing tool.
- Wire endpoints and bends cannot yet be interactively selected and edited.
- There is no explicit junction object or topology-aware wire editing.
- The current connectivity analyzer is geometric; it needs dedicated tests for terminal snapping, wire-to-wire contact, T-junctions, crossings, rotations, and near-miss tolerances.
- There is no electrical highlight/selection of a whole net.

### Circuit and project model
- A project currently contains one circuit scene.
- There are no multiple named circuits/tabs within a project.
- There is no reusable hierarchical subcircuit definition, port declaration, custom-component library entry, or nested circuit editor.
- A single circuit can be named and renamed; the name is persisted separately from the file path. Multiple named circuits within one project remain unavailable.
- Version 2 project files are supported, with a compatibility loader for version 1.

### Measurement and analysis
- No ammeter, voltmeter, multimeter, oscilloscope or logic analyzer is implemented.
- There is no persistent probe/trace system.
- No voltage/current/power/temperature overlay exists.
- No short-circuit, overcurrent, reverse-bias, floating-node or component-rating diagnostics exist beyond basic connectivity and matrix errors.
- No simulation timeline, pause/resume/step/speed controls, or result history exists.

### Reliability and validation
- Automated tests are authored for engineering-value parsing, Gaussian elimination, empty-scene rejection, unsupported-model rejection, dangling-wire handling, named project persistence, v1 compatibility, reactive DC models, and moved-wire connectivity. They have not yet been executed in this remote editing session.
- There are still no tests for full netlist topology, circuit persistence, component behavior, source polarity, Ohm's law, KCL/KVL, nonlinear convergence, or transient accuracy.
- GUI interaction has not been verified automatically.
- No crash recovery/autosave or project backup/version history exists.

## Implementation sequence

The following sequence is deliberate. Later systems depend on earlier ones; adding UI controls before their underlying model would create nonfunctional features.

### Phase A — circuit data model and topology
- Introduce a project document containing multiple independently named circuits.
- Add create, rename, duplicate, reorder, delete and switch-active-circuit operations.
- Give every component a stable instance ID and a user-editable reference/name.
- Replace implicit scene-only persistence with a versioned project schema and migration from the current format.
- Model terminals, wires, junctions and nets explicitly.
- Add interactive wire routing, endpoint dragging, bend editing, snapping, splitting, joining and junction editing.
- Make topology changes undoable and testable.

### Phase B — electrical engine
- Establish one component-model interface: terminal count, parameter schema, validation, DC stamping, transient stamping, state update, ratings and diagnostics.
- Add strict unit-aware parameter parsing and validation.
- Complete resistors and ideal/non-ideal sources first; validate against analytical circuits.
- Add capacitor/inductor transient state and a stable integration method.
- Add diode and LED nonlinear models with Newton iteration and convergence reporting.
- Add BJT and MOSFET models with explicit model/parameter choices and documented approximations.
- Add potentiometer, fuse, switch and battery models.
- Add AC source waveforms and transient excitation.
- Add thermal/electrical stress and failure behavior only after electrical quantities are reliable.

### Phase C — instruments and analysis
- Add probes bound to stable net/component-terminal IDs.
- Add voltage and current meters with correct circuit insertion/measurement semantics.
- Add multimeter modes and an oscilloscope with time traces.
- Add power, energy and temperature measurements where the model supports them.
- Add logic analysis only for explicitly digital/logic-level signals.
- Add diagnostic reports for floating nodes, shorts, overloads, reverse polarity, model limitations and convergence failures.

### Phase D — simulation workflow
- Add start, stop, pause, resume, single-step, reset and speed controls.
- Separate solver time from wall-clock/UI time.
- Preserve simulation snapshots and measurement history.
- Support safe parameter edits during simulation with explicit model-state handling.
- Display simulation status and errors without hiding partial/non-converged states.

### Phase E — hierarchical custom circuits
- Allow selecting a group of components and saving it as a named custom circuit.
- Require explicit external ports and map those ports to internal terminals.
- Store the custom circuit definition independently from each placed instance.
- Place custom circuits as normal components with terminals and editable instance properties.
- Open the internal definition in an editor.
- Define explicit semantics for applying internal edits to active instances and for session-only overrides.
- Prevent recursive circuit definitions and validate port connectivity.

### Phase F — verification and usability
- Add unit, integration, property-based and regression tests.
- Compare canonical circuits against hand calculations and trusted reference results.
- Add project recovery, autosave and backups.
- Profile solver and rendering separately.
- Document model assumptions and supported operating regions per component.

## Completion rule

A checklist item is complete only when its underlying behavior exists, persists correctly where relevant, has automated tests at the appropriate level, and is reachable from the UI. A symbol or placeholder control alone does not qualify.


## Recent implementation increments

- Component names can now be edited in the properties panel; rename operations participate in undo/redo.
- Project format version 2 persists component names and still reads version 1 files. Loading rejects unknown component types before replacing the current scene.
- DC steady-state analysis now models ideal capacitors as open circuits and ideal inductors as zero-volt branches (short circuits), reporting capacitor voltage and inductor current. This is not transient analysis.
- Added tests for named component persistence, legacy file loading, safe rejection of unknown component types, and ideal reactive DC behavior. These tests have been authored but not executed in this remote editing session.


### Latest editing and project increments

- Whole-wire movement now works through normal graphics-item selection and movement; wire position is included in project persistence and clipboard duplication. Netlist geometry is evaluated in scene coordinates after movement.
- A circuit can be renamed from the palette menu. Its name is stored in the project document and restored on load.
- The properties panel now edits component instance names and the workspace records these changes in undo/redo history.
