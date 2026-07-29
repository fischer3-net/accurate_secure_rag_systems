# SDLC Handbook – Secure Development Lifecycle

## 1. Introduction

This handbook defines the mandatory gates and practices for all software and data-flow related systems.

## 2. Requirements Phase

### 2.1 Security Requirements Elicitation

All systems that process sensitive data must identify trust boundaries and external entities during the requirements phase.

## 3. Design Phase

### 3.1 Architecture Review Gate

Before implementation begins, a formal Architecture Review must be completed. The review shall examine:

- All data flows that cross trust boundaries
- Classification of data stores
- Authentication and authorization of external entities

#### 3.1.1 Trust Boundary Analysis

Every data flow that crosses a trust boundary requires explicit documentation of the protection mechanisms in place. Unprotected flows are prohibited.

#### 3.1.2 External Entity Controls

External entities must be authenticated and authorized according to the principle of least privilege. Direct write access from external entities to internal data stores is forbidden without an intermediate process.

## 4. Implementation Phase

### 4.1 Secure Coding Standards

Implementation must follow the approved secure coding checklist. Data flow related controls from the Design Phase remain mandatory.

## 5. Verification Phase

### 5.1 Security Testing Gate

All DFDs and implemented flows must be re-validated against the original Architecture Review findings.
