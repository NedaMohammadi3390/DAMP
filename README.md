# 🚀 DAMP: Detection of Anti-Patterns in Microservices

[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Build](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Java](https://img.shields.io/badge/Java-1.8-blue)]()
[![Platform](https://img.shields.io/badge/platform-Java%2FCLI-lightgrey)]()

DAMP is an automated analysis tool for extracting architectural information from microservice-based systems and detecting **15 microservice antipatterns**.  
This repository also serves as the **replication package** for our study, enabling other researchers to reproduce all experiments end-to-end.

---

## 📘 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Repository Structure](#-repository-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
  - [1. Run Extractor](#1-run-extractor)
  - [2. Run Detector](#2-run-detector)
- [Replication Package](#-replication-package)
- [Sample Output](#-sample-output)
- [Citing DAMP](#-citing-damp)
- [Contributing](#-contributing)
- [Contact](#-contact)

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

