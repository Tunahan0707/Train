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
- [ ] Resistor
- [ ] Capacitor
- [ ] Inductor

### Semiconductors
- [ ] Diode
- [ ] LED
- [ ] BJT transistor
- [ ] MOSFET

### Protection and adjustable components
- [ ] Fuse
- [ ] Potentiometer

### Power sources
- [ ] DC voltage source
- [ ] AC voltage source
- [ ] Battery

### Control and connectivity
- [ ] Switch
- [ ] Wire
- [ ] Connection/junction point
- [ ] Ground reference (GND)

## 3. Measurement Instruments

- [ ] Ammeter
- [ ] Voltmeter
- [ ] Multimeter
- [ ] Oscilloscope
- [ ] Logic analyzer

## 4. Circuit Editing Tools

- [ ] Select and place components.
- [ ] Draw wires and create connections.
- [ ] Delete and edit connections.
- [ ] Move and rotate components.
- [ ] Copy and paste components or selections.
- [ ] Zoom in/out and pan around the workspace.
- [ ] Support selection, multi-selection, and deletion.
- [ ] Save, open, and duplicate circuits.

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

- [ ] Provide a properties panel for components.
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
- [ ] Save projects, open them, and use Save As.
- [ ] Import and export circuits.
- [ ] Allow the component library to be extended.
- [ ] Provide autosave and recovery after a crash.
- [ ] Keep different versions of circuits/projects.

## 12. Visual Design and User Experience

- [ ] Dark and light themes.
- [ ] Customizable workspace.
- [ ] Drag-and-drop component library.
- [ ] Component search and categories.
- [ ] Keyboard shortcuts.
- [ ] Customizable panels.
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

## Scope Notes

- This checklist captures accepted product-level decisions only.
- It does not imply that every listed feature must be implemented in the first milestone.
- Implementation order, exact UI layout, detailed numerical methods, file formats, and other unconfirmed technical choices remain open until discussed and accepted.
