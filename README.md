# 🚀 DAMP: Detection of Anti-Patterns in Microservices

DAMP is an automated analysis tool for extracting architectural information from microservice-based systems and detecting **15 microservice antipatterns**.  
This repository also serves as the **replication package** for our study, enabling other researchers to reproduce all experiments end-to-end.

---

## 📖 Overview

DAMP provides:
- Automated extraction of microservice architecture meta-models  
- Detection of 15 well-known microservice antipatterns  
- Complete support for replicating and validating the results of our research  
- A sample microservice system (*Apollo*) for immediate execution and experimentation  

---

## ✨ Features

- **Extractor Module**  
  Automatically extracts the structural and behavioral characteristics of a microservice system and produces its meta-model.

- **Detector Module**  
  Implements detection rules for 15 microservice antipatterns and generates a full detection report.

- **Fully Automated Workflow**  
  From extraction to detection—no manual steps required.

- **Ready-to-Use Example Project**  
  The *Apollo* system is included for direct execution.

---

## 📁 Repository Structure

```
DAMP/
├── Extractor/
│   ├──  (code for extracting meta-models)
│
├── Detector/
│   ├── (antipattern detection logic)
│
├── projects/
│   └── apollo/   (sample system for replication)
│
└── result-of-analysis/
    └── (generated meta-models and detection reports)
```
