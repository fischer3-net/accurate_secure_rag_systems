# Technical Security Baseline – Data Flow & Trust Controls

## SEC-DFD-001 – Trust Boundary Definition

Every system must explicitly identify and document all trust boundaries. A trust boundary exists wherever data or control passes between entities of different trust levels.

**Risk Tier:** Critical  
**SDLC Phase:** Design

## SEC-DFD-014 – External Entity Access

External entities shall not have direct write access to internal data stores. All such access must be mediated by an authenticated and authorized process.

**Risk Tier:** Critical  
**SDLC Phase:** Design, Implementation

## SEC-DFD-022 – Data Store Classification

All data stores must be classified according to data sensitivity. Classification drives encryption, access control, and monitoring requirements.

**Risk Tier:** High  
**SDLC Phase:** Requirements, Design

## SEC-DFD-031 – Data Flow Integrity

Data flows that cross trust boundaries must provide integrity protection (e.g., TLS, message authentication) appropriate to the risk tier of the data.

**Risk Tier:** High  
**SDLC Phase:** Design, Implementation

## SEC-DFD-045 – Process Isolation

Processes that handle data from different trust levels should be isolated unless a formal risk acceptance is recorded.

**Risk Tier:** Medium  
**SDLC Phase:** Design, Implementation
