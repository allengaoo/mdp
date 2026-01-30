# MDP Ontology Concepts (Based on Palantir Foundry)

## 1. The Ontology Layer

The Ontology is the semantic layer that connects raw data to business applications. It translates technical schemas (tables, columns) into business concepts (objects, properties, links).

In MDP V3 Architecture:
- **Logical Layer**: Defined by `ObjectTypeDef` (immutable identity) and `ObjectTypeVer` (versioned configuration).
- **Physical Layer**: Mapped to `mdp_raw_store` tables via `ObjectMappingDef` and `LinkMappingDef`.
- **Context Layer**: Projects bind to specific versions of objects via `ProjectObjectBinding`.

## 2. Object Types (Noun)

Represents a class of real-world entities (e.g., `Aircraft`, `Employee`, `Ticket`).

### Core Components
- **Primary Key**: A property that uniquely identifies each instance (e.g., `aircraft_tail_number`).
- **Backing Dataset**: The physical table containing the data. In MDP, this is managed via the **Connectivity Layer** (Sync Jobs -> Raw Store -> Mapping).
- **Properties**:
    - **Local Properties**: Specific to this object type, mapped directly from the backing table.
    - **Shared Properties**: References to global standard definitions (`SharedPropertyDef`), ensuring semantic consistency across the enterprise (e.g., multiple objects using the same `currency_code` definition).

## 3. Link Types (Verb)

Defines relationships between object types.

### Cardinality & Implementation

| Cardinality | Meaning | MDP Implementation |
| :--- | :--- | :--- |
| **1:1 (One-to-One)** | Direct extension or unique relation. | **Foreign Key**. Configured in `LinkTypeVer`. |
| **1:N (One-to-Many)** | Hierarchy or ownership (e.g., Airline -> Aircraft). | **Foreign Key**. Configured in `LinkTypeVer`. The "Many" side holds the FK to the "One" side. |
| **M:N (Many-to-Many)** | Network relationships (e.g., Student <-> Course). | **Join Table**. Requires a `LinkMappingDef` that points to a physical intermediate table containing FKs to both source and target. |

## 4. Action Definitions (Intent)

Actions are the mechanism for **capturing business intent** and modifying data. They are the only write-path into the Ontology.

### Philosophy
- **Not just CRUD**: Actions are transactional and semantic. Instead of "Update Row", use "Submit Review".
- **Validation**: Actions enforce rules (e.g., "Cannot approve own request").
- **Side Effects**: Actions can trigger notifications, webhooks, or complex calculations.

### MDP Implementation
- **Function-Backed Actions**: MDP V3 uses Python functions (`FunctionDefinition`) to execute action logic.
- **Execution Flow**:
  1. User submits Action Form (Frontend).
  2. API receives parameters.
  3. `function_runner` executes the bound Python code.
  4. Code performs DB operations (via SQLModel).
  5. System logs the event to `sys_action_log`.

## 5. Functions (Logic)

Functions are code units that encapsulate business logic.

### Types
1.  **Ontology Functions (Read/Compute)**:
    - Used for computed properties or complex queries.
    - Example: `calculate_risk_score(flight_object)`.
2.  **Action Functions (Write/Execute)**:
    - Backing logic for Actions.
    - Example: `create_maintenance_order(plane_id, date)`.

### Relationship: Action vs. Function
- **Action** is the **Interface**: Defines parameters, permissions, and UI presentation.
- **Function** is the **Implementation**: Defines *how* the data changes.
- In MDP, an `ActionDefinition` links to a `FunctionDefinition` via `backing_function_id`.
