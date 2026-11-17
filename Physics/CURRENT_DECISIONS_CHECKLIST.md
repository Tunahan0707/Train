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
- [x] Resistor
- [x] Capacitor
- [x] Inductor

### Semiconductors
- [x] Diode
- [x] LED
- [x] BJT transistor
- [x] MOSFET

### Protection and adjustable components
- [x] Fuse
- [x] Potentiometer

### Power sources
- [x] DC voltage source
- [x] AC voltage source
- [x] Battery

### Control and connectivity
- [x] Switch
- [x] Wire
- [ ] Connection/junction point
- [x] Ground reference (GND)

## 3. Measurement Instruments

- [ ] Ammeter
- [ ] Voltmeter
- [ ] Multimeter
- [ ] Oscilloscope
- [ ] Logic analyzer

## 4. Circuit Editing Tools

- [x] Select and place components.
- [x] Draw wires and create connections.
- [ ] Delete and edit connections.
- [x] Move and rotate components.
- [ ] Copy and paste components or selections.
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

- [ ] Inspect voltage at circuit connections.
- [ ] Inspect current through components.
- [ ] Monitor power and temperature.
- [ ] Detect conditions such as short circuits, overcurrent, and reverse connection where applicable.
- [ ] Identify damaged components and explain the cause of damage.
- [ ] Preserve simulation history for later inspection.
- [ ] Visualize electrical values using colors where useful.

## 11. Project and File Management

- [ ] Support multiple circuits within one project.
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

The current prototype includes schematic symbols and basic editing for the checked components above. Their displayed values are editable, but this does **not** mean their full physical models are implemented. A basic endpoint/T-junction netlist analyzer and a linear DC operating-point solver for resistors with ideal DC voltage sources are implemented. Nonlinear/transient simulation, most component models, and measurement tools remain unimplemented.

Grid snapping, rotation, grouped duplication, JSON-based project save/load, a component properties panel, and visual orthogonal wire drawing with endpoint snapping are implemented in the current editor prototype. The wires are not yet part of an electrical netlist: visual contact does not currently mean the simulator recognizes an electrical connection.

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
- Selected components can be dragged onto the trash target.
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
- Component value annotations were removed from the canvas; values remain editable in the properties panel. This removes the stray-looking default resistor annotation (1000 Ω) from below its symbol.


## Recent functional fixes
- Component palette entries are restored as bordered, filled tiles rather than bare text labels.
- The component drawer uses a horizontal scroll viewport sized to its contents; entries remain inside the available viewport and can be reached by scrolling.
- The canvas (workspace) scrollbars now have explicit theme styling: navy tracks in dark mode, pale grey tracks in light mode, and muted grey handles in both.
- The schematic switch toggles open/closed on click without treating a drag as a toggle. Its state is shown in the properties panel, saved in project files, and copied when duplicated.
- Closed ideal switches join their two terminals in the netlist and are treated as closed connections by the linear DC solver. Open switches remain electrically disconnected and are reported as unsupported by the current DC solver.
