# [Feature Name] Specification

> **Purpose:** Define what the system should do for [feature name]. This is the source of truth for requirements.

## User Scenarios

List independently testable user scenarios, ordered by priority.

### P1 - Must Have

#### Scenario: [Scenario name]
**As a** [user type]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**
- Given [initial context]
- When [action is taken]
- Then [expected outcome]
- And [additional outcome]

### P2 - Should Have

#### Scenario: [Scenario name]
**As a** [user type]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**
- Given [initial context]
- When [action is taken]
- Then [expected outcome]

### P3 - Nice to Have

#### Scenario: [Scenario name]
<!-- Define after P1 and P2 are implemented -->

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F1 | [Requirement description] | P1 |
| F2 | [Requirement description] | P2 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NF1 | Performance | [e.g., page load < 2s] |
| NF2 | Availability | [e.g., 99.9% uptime] |
| NF3 | Security | [e.g., all endpoints authenticated] |

## Key Entities

<!-- Describe the main data structures and their relationships -->

### [Entity Name]

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| [field] | [type] | [description] |

## Success Criteria

### User Success
- [ ] [Measurable user outcome]
- [ ] [User satisfaction metric]

### Business Success
- [ ] [Business metric target]
- [ ] [Adoption or usage target]

### Technical Success
- [ ] All P1 scenarios pass automated tests
- [ ] Performance targets met
- [ ] No critical security issues

## Out of Scope

The following are explicitly NOT included in this specification:
- [Excluded item 1]
- [Excluded item 2]

## Open Questions

- [ ] [Question that needs resolution before implementation]
- [ ] [Dependency that needs clarification]

## Dependencies

- [System or service this depends on]
- [Team or person that needs to be consulted]
