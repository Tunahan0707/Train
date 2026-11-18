# Current Decisions Checklist

> Status: Accepted product-scope decisions
>
> This document records decisions explicitly accepted during planning. It is a scope checklist, not an implementation specification. Details that have not yet been decided should remain open rather than being assumed.

## 1. Core Principles

- [ ] Aim to model real electronic behavior as closely as practical.
- [ ] Avoid unnecessary computational and development cost.
- [ ] Develop the simulation engine and user interface together, rather than postponing the UI until the engine is complete.
- [ ] Keep visual effects independent from the electrical simulation so that effects can be disabled without affecting simulation correctness.
- [ ] Do not silently sacrifice physical accuracy for performance. If a model is simplified, make that limitation visible to the user.

## 2. Initial Component Library

### Passive components
- [x] Resistor symbol and basic value field
- [x] Ideal resistor DC model and V/I/P calculation
- [ ] Ratings, tolerance and thermal behavior
- [x] Capacitor symbol and basic value field
- [x] Ideal capacitor DC steady-state open-circuit model
- [ ] Transient charging/discharging, ESR, leakage and voltage limits
- [x] Inductor symbol and basic value field
- [x] Ideal inductor DC steady-state short-circuit model
- [ ] Transient response, winding resistance and saturation

### Semiconductors
- [x] Diode symbol
- [x] Approximate piecewise-linear DC forward/reverse model
- [ ] Full device curves, reverse breakdown and temperature dependence
- [x] LED symbol
- [x] Approximate piecewise-linear DC conduction model
- [ ] Optical output, full device curves and ratings
- [x] BJT symbol
- [x] Simplified threshold-controlled DC switch approximation
- [ ] BJT base current, gain and operating-region model
- [x] MOSFET symbol
- [x] Simplified gate-threshold-controlled DC switch approximation
- [ ] MOSFET transfer/output curves, body diode and operating-region model

### Protection and adjustable components
- [x] Fuse symbol
- [x] Fixed-resistance DC fuse approximation
- [ ] Fuse current/time, thermal and failure model
- [x] Potentiometer symbol
- [x] Three-terminal resistance divider with editable wiper ratio
- [ ] Wiper contact resistance and non-ideal behavior

### Power sources
- [x] DC voltage source symbol
- [ ] DC source internal resistance, current limit and source parameters
- [x] AC voltage source symbol
- [ ] AC waveform and transient source model
- [x] Battery symbol
- [ ] Battery internal resistance, capacity and discharge model

### Control and connectivity
- [x] Switch symbol, manual open/close state, and undo/redo
- [ ] Switch contact resistance, timing and transient behavior
- [x] Wire drawing and basic geometric connectivity analysis
- [ ] Editable wire endpoints, junction editing and robust topology validation
- [ ] Connection/junction point component
- [x] Ground reference symbol and shared reference-node handling

## 3. Measurement Instruments

- [ ] Ammeter
- [ ] Voltmeter
- [ ] Multimeter
- [ ] Oscilloscope
- [ ] Logic analyzer

## 4. Circuit Editing Tools

- [x] Select and place components.
- [x] Draw schematic wires and infer basic terminal/wire-segment connectivity.
- [x] Draw orthogonal wires by clicking start and end points with terminal/wire snapping.
- [ ] Select, move, reshape, split, join and delete wires.
- [ ] Add and edit explicit junction points.
- [ ] Validate dangling, shorted and ambiguous connections.
- [x] Move and rotate components.
- [x] Copy and paste components or selections (Ctrl+C / Ctrl+V).
- [x] Duplicate selected components or selections.
- [x] Zoom in/out and pan around the workspace.
- [x] Support selection, multi-selection, and deletion.
- [x] Save and open circuits.
- [ ] Duplicate complete circuits.

## 5. Reusable Custom Components

- [ ] Save a user-created circuit as a reusable custom component.
- [ ] Define the custom component's input and output terminals.
- [ ] Place and use custom components in other circuits.
- [ ] Open and inspect a custom component's internal circuit.
- [ ] Edit the internal circuit.
- [ ] Apply internal edits immediately during an active simulation, without requiring a simulation restart.
- [ ] Allow internal edits to be either saved permanently to the custom component or kept only for the current simulation session.
- [ ] Session-only edits must not modify the original saved custom component.

## 6. Circuit Views

- [ ] Breadboard view.
- [ ] Schematic view.
- [ ] Both views represent the same circuit; edits in one view are reflected in the other.

## 7. Simulation Controls

- [ ] Start and stop simulation.
- [ ] Pause and resume simulation.
- [ ] Advance simulation one step at a time.
- [ ] Adjust simulation speed.
- [ ] Reset simulation time.
- [ ] Change component values during simulation where supported.
- [ ] Display errors and damage notifications.

## 8. Component Properties and Models

- [x] Provide a properties panel for components.
- [ ] Expose relevant physical parameters, not only idealized values.
- [ ] Support general parameter-based component configuration.
- [ ] Support importing or using real component models and manufacturer data where practical.

Examples of relevant properties discussed:
- Resistors: resistance, tolerance, power rating, temperature.
- Capacitors: capacitance, voltage rating, ESR, leakage.
- Transistors: model and operating parameters, including temperature-related behavior.
- Power sources: voltage, internal resistance, current limit.
- Fuses: rated current and time/current behavior.

These are examples of intended modeling detail, not a finalized parameter schema for every component.

## 9. Damage and Visual Effects

- [ ] Model component stress and damage based on electrical behavior.
- [ ] Support overheating, failure, burning, smoke, sparks, and explosions where appropriate.
- [ ] Damaged components may remain in the circuit but behave differently or stop conducting, depending on the failure mode.
- [ ] Use lightweight animations or prepared effects rather than expensive particle/physics simulation by default.
- [ ] Keep effects optional and independently adjustable.
- [ ] Visual effects must not determine or replace the electrical simulation result.

## 10. Analysis and Debugging

- [ ] Probe voltage at arbitrary circuit connections.
- [x] Inspect calculated voltage/current/power for supported components after DC solve.
- [ ] Monitor temperature.
- [ ] Detect conditions such as short circuits, overcurrent, and reverse connection where applicable.
- [ ] Identify damaged components and explain the cause of damage.
- [ ] Preserve simulation history for later inspection.
- [ ] Visualize electrical values using colors where useful.

## 11. Project and File Management

- [x] Support multiple named circuits within one project.
- [x] Save projects, open them, and use Save As.
- [ ] Import and export circuits.
- [ ] Allow the component library to be extended.
- [ ] Provide autosave and recovery after a crash.
- [ ] Keep different versions of circuits/projects.

## 12. Visual Design and User Experience

- [ ] Dark and light themes.
- [ ] Customizable workspace.
- [ ] Drag-and-drop component library.
- [x] Component search and categories.
- [x] Keyboard shortcuts.
- [x] Customizable panels.
- [ ] Animated electrical-flow indicators.
- [ ] Color changes that communicate circuit/component state.
- [ ] Zoomable detailed component views.
- [ ] Adjustable visual-effect and animation intensity.
- [ ] Ability to disable effects and animations.

## 13. Performance and Numerical Reliability

- [ ] Optimize calculations according to circuit size.
- [ ] Provide a configurable balance between simulation accuracy and performance.
- [ ] Offer more detailed physical models optionally.
- [ ] Provide performance monitoring for large circuits.
- [ ] Allow expensive visual effects to be disabled independently.
- [ ] Report simulation stability and convergence problems.
- [ ] Explain calculation errors in understandable terms.

## 14. Explicitly Deferred

- [ ] Sound system and sound effects.
- [ ] Educational/help system, tutorials, and interactive guides.

These topics are deferred for now and are not part of the current agreed scope.

---

## Implementation Notes

The DC numeric foundation validates engineering-notation values, rejects non-finite inputs and malformed linear systems, and has standard-library unit tests for suffix parsing and Gaussian elimination. These tests do not yet replace end-to-end circuit simulation tests.

The current prototype has schematic symbols for the listed component families; symbols and editable nominal values are not complete physical models. The netlist analyzer joins wire endpoints, component terminals, shared ground references and contacts to wire segments. Wire crossings without endpoint contact are not connected. The linear DC solver currently supports resistors, ideal DC voltage sources, batteries and ideal closed switches. It now rejects unsupported component types instead of silently presenting a partial solution. This is still a narrow DC solver: nonlinear semiconductor models, transient behavior, AC analysis, component ratings/failure, and measurement instruments are not implemented.

The editor currently stores one schematic scene per project file. It does not yet support a multi-circuit project, named/reorderable circuit tabs, reusable hierarchical subcircuits, custom component ports, or editing a saved subcircuit definition. Wires are drawn as fixed orthogonal paths; interactive endpoint editing/routing and junction objects are not implemented. Project persistence is JSON-based and currently stores component types, positions, rotations, values and switch state.

Grid snapping, component rotation, grouped duplication, basic project save/load, a component properties panel, and schematic connectivity analysis exist. These are prototype capabilities and must not be interpreted as a finished circuit-design/simulation workflow.

## Scope Notes

- This checklist captures accepted product-level decisions only.
- It does not imply that every listed feature must be implemented in the first milestone.
- Implementation order, exact UI layout, detailed numerical methods, file formats, and other unconfirmed technical choices remain open until discussed and accepted.


## Recent interface changes

- The component side dock has been replaced with a bottom category bar and an upward-expanding, horizontally scrollable component drawer.
- The bottom bar starts with the Menu button, followed by component category tabs.
- Components can be dragged into the workspace or inserted at the viewport center by clicking.
- Holding Shift while clicking inserts vertically aligned components and keeps the stack selected.
- The category drawer closes after ordinary click insertion or drag-and-drop; Shift insertion keeps it open.
- The canvas grid rendering has been removed; grid snapping remains enabled.
- Properties are shown in the right panel as inline values without boxed input fields.
- Multi-selection groups matching component types so one value edit applies to all selected components; different types get separate property sections.
- Theme switch includes sun/moon indicators and the interface text follows the active theme.
- Selected components can be dragged onto the trash target; holding Shift changes the target to a broom icon, and Shift-click clears all circuit elements.
- Fullscreen control removed.
- Navy dark/light themes with an animated sliding switch.
- Interface explanatory copy removed; component labels retained.

## Recent interface fixes
- Theme-switch sun/moon symbols now rotate with the moving knob and crossfade during the transition.
- The crescent icon uses a filled crescent shape rather than a static arc.
- Component drawer, scroll area, viewport, tab buttons, property labels, inputs, menus, and dock text use the interpolated active theme colors.
- Light/dark theme application explicitly synchronizes the component drawer scroll viewport palette and stylesheet, preventing a surface-color mismatch in the expanded drawer.
- Property-panel cleanup recursively removes nested row layouts and their widgets, preventing stale values/labels after edits or deselection.
- Editing a shared property sends one batch update for the selected same-type components and refreshes the panel once.
- Mixed values show an empty field with a placeholder instead of retaining one component's old value.
- Component reference names and values are now rendered beneath symbols; both names and values remain editable in the properties panel.


## Recent functional fixes
- Component palette entries use hollow, sharp-cornered tiles; their widths are calculated from full labels and the active style, with a minimum width.
- The component drawer uses a horizontal scroll viewport sized to its contents; component entries are hollow, sharp-cornered tiles with widths calculated from their full labels and a minimum width.
- The canvas (workspace) scrollbars now have explicit theme styling: navy tracks in dark mode, pale grey tracks in light mode, and muted grey handles in both.
- The schematic switch toggles open/closed on click without treating a drag as a toggle. Its state is shown in the properties panel, saved in project files, and copied when duplicated.
- Switch terminals remain distinct in the netlist so switch current can be measured. The DC solver adds an ideal zero-volt branch for a closed switch; an open switch is modeled as an open circuit.
- The DC solver now refuses to produce a partial result when unsupported component types are present or a component terminal is reported disconnected.


## Implemented since the previous audit

- [x] Edit component instance names from the properties panel.
- [x] Undo/redo component renaming.
- [x] Persist component names in project file version 2 while retaining version 1 loading.
- [x] Reject unknown component types before clearing/replacing the active scene.
- [x] Ideal capacitor and inductor DC steady-state behavior.
- [ ] Circuit document naming, multiple circuit documents, and reusable hierarchical circuit definitions.
- [ ] Transient simulation and nonlinear semiconductor models.


## New implemented items

- [x] Rename the active circuit and persist its name.
- [x] Move wire objects and persist their scene position.
- [x] Include moved-wire positions in copy/paste and duplicate operations.
- [x] Rebuild connectivity from moved wire scene coordinates.
- [ ] Interactive wire endpoint and bend editing.
- [ ] Multiple circuit documents and reusable hierarchical circuits.
- [x] Assign stable instance IDs to components and wires.
- [x] Automatically assign unique reference labels to newly placed components.
- [x] Render component reference labels and values on the schematic.

- [x] Multiple named circuit tabs in one project.
- [x] Add, rename, reorder and close circuit tabs.
- [x] Save/load all circuit tabs and restore the active tab.
- [ ] Reusable hierarchical custom circuit definitions with explicit external ports.

- [x] Two-click orthogonal wire drawing tool.
- [x] Snap wire endpoints to component terminals and existing wire segments.
- [x] Preview and Escape cancellation for wire drawing.
- [ ] Individual wire endpoint/bend handles and explicit junction editing.

- [x] Basic piecewise-linear DC diode and LED conduction models.
- [ ] Detailed Shockley/device-curve semiconductor models, temperature and reverse breakdown.

- [x] Show calculated per-component DC readings in the properties panel after simulation.
- [x] Invalidate stale measurements after electrical edits.
- [ ] Dedicated meter instruments and oscilloscope traces.

- [x] Fixed-resistance DC fuse model and measurements.
- [x] Three-terminal potentiometer DC divider with editable, undoable wiper position.
- [ ] Fuse thermal trip and current rating model.

- [x] Simplified DC on/off switch approximations for NPN BJT and N-channel MOSFET.
- [ ] Full BJT/MOSFET device models, gain/transfer curves and parasitics.


## Newly implemented DC scope

- [x] Per-component DC operating-point measurements are visible in the properties panel after a successful solve.
- [x] Circuit edits invalidate old DC measurements.
- [x] Fuse and potentiometer DC approximations are included.
- [x] Approximate diode/LED and transistor switch states are included in DC analysis.

- [x] Report current through closed ideal switches and voltage across open switches.

- [x] Make manual switch state changes undoable and redoable.
