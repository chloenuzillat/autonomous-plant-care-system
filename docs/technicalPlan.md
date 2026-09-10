# Technical Plan

## Project Overview

Build an autonomous mobile robot capable of monitoring a plant's environment, navigating an indoor space, identifying suitable locations for the plant, and learning from the plant's response over time.

The system will combine embedded systems, robotics, computer vision, and machine learning to create a closed loop plant care system.

The core goal is to build an autonomous embodied system that can learn and act on the individual environmental needs of a plant.

## System Architecture

The system is divided between a Raspberry Pi and a microcontroller. The Raspberry Pi handles computation and decision making, while the microcontroller handles hardware control and sensor acquisition.

<img width="1012" height="662" alt="image" src="https://github.com/user-attachments/assets/709dca27-90a2-4e89-9a93-3c0cf71d3afa" />

### Raspberry Pi

- Main computation
- Computer vision
- Navigation and mapping
- Data collection and logging
- Plant modeling
- Decision making

### Microcontroller

- Motor control
- Wheel encoder reading
- Sensor acquisition
- Low level and real time control

The initial microcontroller platform is an **Arduino UNO R4 WiFi**.

### Raspberry Pi and Microcontroller Communication

The initial communication method will be USB serial/UART using a simple command/response interface.

The communication layer should remain modular so the underlying transport can be changed later if needed.

## Major Components

### Embedded System

#### Raspberry Pi

- Computer vision
- Navigation and mapping
- Plant modeling
- Decision making
- Data collection
- Communication with the microcontroller

The Raspberry Pi software will be developed primarily in **Python**.

#### Microcontroller

- Motor control
- Encoder reading
- Environmental sensor acquisition
- Low level control
- Communication with the Raspberry Pi

### Sensors

#### Environmental

- Light
- Temperature
- Humidity
- Soil moisture

#### Robot

- Wheel encoders
- IMU
- Camera
- Ultrasonic obstacle sensor

The exact sensor configuration will be determined through prototyping rather than assuming every sensor is required.

## Robotics Functionality

The robot should progressively support:

1. Drive forward and backward
2. Turn
3. Measure its movement
4. Detect obstacles
5. Estimate its position
6. Navigate to a target location
7. Transport the plant to a selected location

The eventual navigation pipeline is:

**Map -> Current Position -> Target Location -> Path Planning -> Obstacle Avoidance -> Motor Commands**

The system should begin with simple movement and obstacle avoidance before adding advanced localization, mapping, and path planning.

### Robot Model

The robot will use a differential drive model:

- Left motor controls the left wheel
- Right motor controls the right wheel
- Wheel encoders provide movement measurements
- Motor commands are converted into wheel velocities

This model will support later odometry and autonomous navigation.

## Computer Vision

Computer vision will be used for environmental perception and plant monitoring.

### Environment

Potential uses include:

- Detecting obstacles
- Identifying navigable areas
- Assisting localization
- Assisting mapping
- Identifying relevant environmental features

### Plant

Potential capabilities include:

1. Detect the plant
2. Estimate plant size
3. Track growth over time
4. Detect visible stress or health indicators
5. Track visual changes over time
6. Relate visual observations to environmental conditions

Computer vision will be introduced incrementally, beginning with basic detection before more advanced analysis.

## Plant Environmental Model

The robot will maintain a model of the relationship between environmental conditions and plant response.

Initial model:

**Plant Requirements -> Environmental Measurements -> Suitability Score**

As observations accumulate:

**Plant Requirements + Environmental Measurements + Plant Response -> Updated Suitability Model**

The goal is eventually to learn the preferences of the individual plant rather than relying only on generic plant requirements.

Relevant data may include:

- Light exposure
- Temperature
- Humidity
- Soil moisture
- Location
- Time
- Plant growth
- Visible plant health indicators

## Learning and Feedback Loop

The system will use a closed loop process:

**Choose Location -> Move Plant/Robot -> Monitor Environment and Plant -> Evaluate Plant Response -> Update Model -> Choose Next Action**

Development should begin with a simple suitability model and improve as real observations are collected.

Potential approaches include:

- Rule based suitability scoring
- Statistical models
- Supervised machine learning
- Reinforcement learning

The specific machine learning approach will be selected after data collection and a baseline model are working. Machine learning is not required for the initial robot prototype.

## Hardware

The initial prototype will use the hardware already available to the team wherever practical.

## Future Capabilities

Possible extensions include:

- Individualized plant preference learning
- More advanced computer vision
- Autonomous mapping and navigation
- Improved plant health estimation
- Predictive watering
- Automated watering during vacations
- Virtual plant avatar reflecting plant/soil health
- Multiple plant support
- More advanced experimentation and learning strategies
