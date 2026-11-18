# Physics implementation audit

Audit baseline: `physics` branch, 2026-11-18.

This document distinguishes existing prototype behavior from verified engineering capability. A visible symbol, editable text field, or menu entry is not evidence that a physical model or end-to-end workflow is complete.

## Current verified-by-source-code capabilities

- PySide6 schematic editor with selection, multi-selection, placement, drag/drop, rotation, duplication, undo/redo, zoom and pan.
- Symbol definitions for resistor, capacitor, inductor, diode, LED, BJT, MOSFET, fuse, potentiometer, DC source, AC source, battery, switch, ground and wire.
- Movable orthogonal wire graphics and a geometric netlist builder. Wire endpoints, component terminals, ground references and contacts to wire segments can be grouped. A crossing without endpoint contact is not a junction.
- Multi-circuit project tabs with add, rename, reorder and close operations; project format stores multiple named circuit scenes, active circuit ID, and stable circuit/component IDs. Legacy single-circuit formats v1-v3 are importable.
- Inline component value and instance-name editing; new components receive unique reference labels (R1, C1, V1, etc.), labels/values are drawn on the canvas, and rename operations participate in undo/redo.
- Linear DC operating-point analysis using modified nodal analysis for resistors, ideal DC voltage sources, batteries, ideal closed switches (zero-volt MNA branches with measurable current), ideal capacitors (open circuit), ideal inductors (zero-volt branch), fixed-resistance fuses, three-terminal potentiometers, and piecewise-linear diodes/LEDs (fixed forward drop plus series resistance).
- Engineering suffix parsing and Gaussian elimination unit tests.
- Clipboard copy/paste and duplicate operations are present in the workspace code.

## Important limitations found

### Electrical models
- Most component symbols are not backed by electrical equations.
- The current DC solver does not model capacitor/inductor transient response or AC sources. Fuse behavior is a fixed-resistance approximation; potentiometers are modeled as a three-terminal resistive divider. BJT/MOSFET behavior is only an idealized voltage-controlled switch approximation, not a transistor device model. Diode/LED behavior is an approximate piecewise-linear DC model, not a full semiconductor model.
- It has no component tolerance, voltage/current/power ratings, thermal model, internal resistance, current limiting, battery state, or failure model.
- It has no time-domain integrator, nonlinear Newton iteration, convergence controls, or event handling.
- A solver result must never be shown as a complete circuit result when unsupported devices are present. The DC solver was changed to reject unsupported devices rather than silently omit them.

### Connectivity and editing
- A two-click orthogonal wire tool now draws between snapped component terminals or existing wire geometry. Whole wires can be moved. Individual endpoint/bend handles and explicit junction objects are still absent.
- Wire endpoints and bends cannot yet be interactively selected and edited.
- There is no explicit junction object or topology-aware wire editing.
- The current connectivity analyzer is geometric; it needs dedicated tests for terminal snapping, wire-to-wire contact, T-junctions, crossings, rotations, and near-miss tolerances.
- There is no electrical highlight/selection of a whole net.

### Circuit and project model
- A project can contain multiple named circuit scenes in tabs.
- Multiple named circuit tabs now exist; reusable hierarchical custom circuit definitions are still absent.
- There is no reusable hierarchical subcircuit definition, port declaration, custom-component library entry, or nested circuit editor.
- Each circuit tab has a persisted identity and editable name; the active tab is restored when the project is reopened.
- Multi-circuit project schema v1 is supported; legacy single-circuit schema versions 1, 2 and 3 are imported.

### Measurement and analysis
- No physical ammeter, voltmeter, multimeter, oscilloscope or logic analyzer instrument is implemented. Latest DC solver results can be inspected per selected component in the properties panel.
- There is no persistent probe/trace system.
- No voltage/current/power/temperature overlay exists.
- No short-circuit, overcurrent, reverse-bias, floating-node or component-rating diagnostics exist beyond basic connectivity and matrix errors.
- No simulation timeline, pause/resume/step/speed controls, or result history exists.

### Reliability and validation
- Automated tests are authored for engineering-value parsing, Gaussian elimination, empty-scene rejection, unsupported-model rejection, dangling-wire handling, named and multi-circuit project persistence, legacy import, reactive DC models, diode states, and moved-wire connectivity. They have not yet been executed in this remote editing session.
- There are still no comprehensive tests for full netlist topology, all component behaviors, multi-branch KCL/KVL, active-set stability across complex diode networks, or transient accuracy.
- GUI interaction has not been verified automatically.
- No crash recovery/autosave or project backup/version history exists.

## Implementation sequence

The following sequence is deliberate. Later systems depend on earlier ones; adding UI controls before their underlying model would create nonfunctional features.

### Phase A — circuit data model and topology
- [x] Introduce a project document containing multiple independently named circuits.
- [x] Add, rename, reorder, close and switch-active-circuit operations. Circuit duplication remains pending.
- [x] Give every component a stable instance ID and a user-editable reference/name.
- Project-level versioned persistence and migration from legacy single-circuit formats are implemented; topology remains scene-derived.
- Model terminals, wires, junctions and nets explicitly.
- [x] Add click-to-route orthogonal wires with terminal/wire snapping. Endpoint dragging, bend editing, splitting, joining and explicit junction editing remain pending.
- Make topology changes undoable and testable.

### Phase B — electrical engine
- Establish one component-model interface: terminal count, parameter schema, validation, DC stamping, transient stamping, state update, ratings and diagnostics.
- Add strict unit-aware parameter parsing and validation.
- Complete resistors and ideal/non-ideal sources first; validate against analytical circuits.
- Add capacitor/inductor transient state and a stable integration method.
- [x] Add an approximate piecewise-linear DC diode/LED active-set model. Full nonlinear device models and broader convergence validation remain pending.
- Add BJT and MOSFET models with explicit model/parameter choices and documented approximations.
- Add potentiometer, fuse, switch and battery models.
- Add AC source waveforms and transient excitation.
- Add thermal/electrical stress and failure behavior only after electrical quantities are reliable.

### Phase C — instruments and analysis
- Add probes bound to stable net/component-terminal IDs. Component-level DC result display exists, but persistent probes do not.
- Add voltage and current meters with correct circuit insertion/measurement semantics.
- Add multimeter modes and an oscilloscope with time traces.
- Add power, energy and temperature measurements where the model supports them.
- Add logic analysis only for explicitly digital/logic-level signals.
- Add diagnostic reports for floating nodes, shorts, overloads, reverse polarity and component ratings. Basic unsupported-model and solver convergence errors are present.

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
- Project format version 3 persists circuit names, component names, stable component instance IDs and movable wire positions; versions 1 and 2 remain readable. Loading rejects unknown component types before replacing the current scene.
- DC steady-state analysis now models ideal capacitors as open circuits and ideal inductors as zero-volt branches (short circuits), reporting capacitor voltage and inductor current. This is not transient analysis.
- Added tests for named component persistence, legacy file loading, safe rejection of unknown component types, and ideal reactive DC behavior. These tests have been authored but not executed in this remote editing session.


### Latest editing and project increments

- Whole-wire movement now works through normal graphics-item selection and movement; wire position is included in project persistence and clipboard duplication. Netlist geometry is evaluated in scene coordinates after movement.
- A circuit can be renamed from the palette menu. Its name is stored in the project document and restored on load.
- The properties panel now edits component instance names and the workspace records these changes in undo/redo history.

- Stable UUIDs are now assigned to component and wire instances and persisted for future probe/measurement references.


### Multi-circuit project increment

- A project now holds multiple named circuit tabs. Tabs can be added, renamed, reordered, and closed; the active circuit is restored on load.
- Saving writes a project document containing all tabs. Opening legacy single-circuit .physics files imports them as a one-tab project.
- Each circuit and component has a stable UUID. The project loader validates duplicate circuit/component IDs before replacing the active project.
- This is multi-document organization, not yet hierarchical custom circuit components with external ports.

- Wire-tool preview, Escape cancellation, snapping to nearby component terminals/wire segments, and undoable wire creation are implemented.

- Diode and LED DC operating points use an active-set piecewise-linear approximation: off = open circuit; on = fixed forward drop with series resistance. Reverse breakdown, temperature dependence, leakage, capacitance and detailed device curves are not modeled.

- Per-component DC measurements are keyed by stable instance UUID and shown in the properties panel after a successful solve. Editing the circuit invalidates the stored result to prevent stale readings.

- Fuse current/voltage/power are now calculated using the configured fixed resistance; no fuse blowing or thermal rating behavior exists.
- Potentiometers are solved as two resistive sections with an editable 0–1 wiper ratio, persisted in project files and included in undo/redo.

- BJT (NPN) and N-channel MOSFET symbols now have DC on/off switching approximations: BJT threshold 0.7 V, MOSFET gate threshold 2.0 V; conducting output path uses a small fixed resistance. Base/gate current, gain curves, saturation physics, body diode, capacitance and temperature are not modeled.

- Closed switches are now stamped as explicit zero-volt MNA branches instead of merging their terminals in the netlist, so current through a closed switch and voltage across an open switch can be reported.
