# Physics implementation audit

Audit baseline: `physics` branch, 2026-11-18.

This document distinguishes existing prototype behavior from verified engineering capability. A visible symbol, editable text field, or menu entry is not evidence that a physical model or end-to-end workflow is complete.

## Current verified-by-source-code capabilities

- PySide6 schematic editor with selection, multi-selection, placement, drag/drop, rotation, duplication, undo/redo, zoom and pan.
- Symbol definitions for resistor, capacitor, inductor, diode, LED, BJT, MOSFET, fuse, potentiometer, DC source, AC source, battery, switch, ground and wire.
- Basic orthogonal wire graphics and a geometric netlist builder. Wire endpoints, component terminals, ground references and contacts to wire segments can be grouped. A crossing without endpoint contact is not a junction.
- JSON project save/load for one schematic scene.
- Basic inline value editing and a properties panel.
- Linear DC operating-point analysis using modified nodal analysis for resistors, ideal DC voltage sources, batteries and ideal closed switches.
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
- Wire graphics are fixed orthogonal paths, not interactive terminal-to-terminal routes.
- Wire endpoints and bends cannot yet be interactively selected and edited.
- There is no explicit junction object or topology-aware wire editing.
- The current connectivity analyzer is geometric; it needs dedicated tests for terminal snapping, wire-to-wire contact, T-junctions, crossings, rotations, and near-miss tolerances.
- There is no electrical highlight/selection of a whole net.

### Circuit and project model
- A project currently contains one circuit scene.
- There are no multiple named circuits/tabs within a project.
- There is no reusable hierarchical subcircuit definition, port declaration, custom-component library entry, or nested circuit editor.
- There is no renameable circuit identity separate from the file path/window title.
- There is no versioned project migration beyond the current single format version.

### Measurement and analysis
- No ammeter, voltmeter, multimeter, oscilloscope or logic analyzer is implemented.
- There is no persistent probe/trace system.
- No voltage/current/power/temperature overlay exists.
- No short-circuit, overcurrent, reverse-bias, floating-node or component-rating diagnostics exist beyond basic connectivity and matrix errors.
- No simulation timeline, pause/resume/step/speed controls, or result history exists.

### Reliability and validation
- Automated tests cover engineering-value parsing, Gaussian elimination, empty-scene rejection, unsupported-model rejection, and a dangling-wire case.
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
