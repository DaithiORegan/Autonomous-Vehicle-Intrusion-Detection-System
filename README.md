Autonomous Vehicle Intrusion Detection System

CAN Bus Security | Machine Learning | Attack Simulation | Automotive Cybersecurity

Project Overview

Developed a Python-based automotive cybersecurity testing environment to investigate vulnerabilities in autonomous vehicle communication systems and evaluate machine-learning approaches to intrusion detection.

The project explores how malicious Controller Area Network (CAN) traffic can affect vehicle systems, combining attack simulation, network traffic analysis, anomaly detection and autonomous vehicle telemetry.

Core objectives:

Simulate and investigate malicious automotive network activity.

Analyse CAN traffic patterns to identify suspicious behaviour.

Apply machine-learning techniques to detect anomalous traffic.

Examine relationships between cyberattacks and autonomous vehicle system behaviour.

Evaluate detection methods using collected traffic data and performance metrics.

Technical Skills Demonstrated

Category

Technologies and Skills

Programming

Python, automation, data processing

Cybersecurity

Intrusion detection, attack simulation, traffic analysis

Networking

CAN bus, SocketCAN, message inspection

Machine Learning

Isolation Forest, anomaly detection, feature engineering

Data Analysis

Dataset generation, anomaly scoring, evaluation

Simulation

CARLA, vehicle telemetry, adversarial testing

Computer Vision

OpenCV, image degradation, perception analysis

System Components

1. CAN Bus Attack Simulation

Built a controlled environment for investigating CAN communication vulnerabilities, including message spoofing, replay attacks and denial-of-service scenarios.

2. Machine-Learning Intrusion Detection

Developed an anomaly-detection workflow using traffic-derived features to identify deviations from expected CAN communication patterns.

3. Autonomous Vehicle Simulation

Integrated vehicle telemetry and attack-related scripts to investigate how manipulated signals and malicious activity can influence simulated vehicle behaviour.

4. Perception Security Analysis

Explored visual degradation scenarios and their effects on computer vision systems, investigating the relationship between network-level attacks and perception reliability.

5. Security Evaluation

Implemented scripts for dataset preparation, detection evaluation and contextual analysis to support repeatable experiments and comparison of detection behaviour.

Project Evidence and Results

This section will contain verified experimental results, including:

Detection performance and false-positive analysis.

CAN traffic captures and anomaly-score visualisations.

Comparisons between normal and malicious traffic.

Simulation screenshots and attack demonstrations.

Observed limitations and potential improvements.

Repository Structure

The Thesis/canSim/ directory contains the primary simulation, dataset preparation, attack and evaluation scripts.

Notable files include:

build_dataset.py — dataset preparation

evaluate.py — evaluation workflow

evaluate_contextual.py — contextual evaluation

contextual_ids.py — contextual intrusion detection

carla_telemetry.py — CARLA telemetry integration

carla_spoof_attack.py — spoofing simulation

carla_visual_attack.py — visual attack testing

carla_attack_impact.py — attack-impact investigation

Project Context

Developed as a final-year BSc (Hons) IT Management & Cybersecurity project, focusing on practical automotive security research, experimental attack simulation and machine-learning-based threat detection.

The project demonstrates transferable skills relevant to security operations, threat detection engineering, network security, Python development and technical security analysis.