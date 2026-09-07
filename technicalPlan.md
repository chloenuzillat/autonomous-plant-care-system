# Technical Plan

## Project Overview

Build an autonomous mobile robot capable of monitoring a plant's environment, navigating an indoor space, identifying suitable locations for the plant, and learning from the plant's response over time.

The system will combine embedded systems, robotics, computer vision, and machine learning to create a closed-loop plant care system.

## System Architecture

<img width="1012" height="662" alt="image" src="https://github.com/user-attachments/assets/709dca27-90a2-4e89-9a93-3c0cf71d3afa" />

## Major Components

### Embedded System 

Raspberry Pi
- Computation
- Computer vision
- Navigation
- Data collection
- Plant Modeling
- Decision making

Microcontroller
- Motor control
- Encoder reading
- Sensor aquisition
- Real time control

Communication
- Raspberry Pi <-> Microcontroller
- Initially UART (Universal Asynchronous Receiver/Transmitter)/serial (potentially another protocol later)

### Sensors

Environmental
- Light sensor
- Temperature sensor
- Humidity sensor
- Soil moisture

Robot
- Wheel encoders
- IMU
- Camera
- LiDAR/depth sensor

## Robotics Functionality

1. Drive forward/backward
2. Turn
3. Measure its movement
4. Detect obstacles
5. Determine its position
6. Navigate to a target location

Evnetually:
Map -> Current Position -> Target Location -> Path Planning -> Obstacle Avoidance -> Motor Commands

## Computer Vision Functionality

### Environement

1. Assist environmental perception
3. Potentially assist localization/mapping

### Plant

1. Detect the plant
2. Estimate plant size
3. Monitor growth
4. Detect visible stress/health indicators
5. Track changes over time

## Plant Environmental Model

Plant requirements -> Environmental measures -> Suitability score -> Plant response -> Update model

## Learning/Feedback Loop

Choose location -> Move plant/robot -> Monitor plant & environment -> Evaluate plant response -> Update model -> Choose next location

## Development Plan

### Phase 0 - Simulation & Software Foundation

Goal: Start developing before buying expensive hardware (I need time + more money, sorry)
- Define sensor data format
- Define robot command interface
- Create plant/environment data model
- Create basic plant model
- Build data logging system
- Create simulated environment
- Simulate robot position/movement
- Implement basic suitability scoring
- Start experimenting with how plant responses will be represented

### Phase 1 - Mobile Platform

!!! Note: This phase will be expensive due to hardware costs, so it may take some time after Phase 0 to begin Phase 1 (I need time + money to get the hardware required) !!!

Goal: Robot can reliably move
- Build chassis
- Motors
- Motor driver
- Battery
- Microcontroller
- Raspberry Pi
- Pi <-> Microcontroller communication

Needs to be purchased:
- Chassis/platform
- 2 wheels
- Caster wheel
- 2 × DC gear motors with wheel encoders
- Motor driver
- Microcontroller
- Battery (for motors)
- 5V voltage regulator / power supply for Raspberry Pi
- Jumper wires
- Motor wires/connectors
- Breadboard
- Screws/nuts/standoffs
- Basic brackets or mounts for the Pi, MCU, and motor driver
- USB cable

### Phase 2 - Environmental Sensing

Goal: Robot can measure its environment
- Light
- Temperature
- Humidity
- Soil moisture
- Data logging

### Phase 3 - Navigation

Goal: Robot can autonomously move through its environment
- Encoders
- IMU
- Obstacle detection
- Localization
- Mapping
- Path planning

### Phase 4 - Plant Monitoring

Goal: Robot can observe the plant
- Camera
- Plant detection
- Growth tracking
- Visual health indicators
- Environmental correlation

### Phase 5 - Intelligent Placement

Goal: Robot determines where plant should go
- Plant requirements
- Environmental map
- Plant observations
- Location prediction
- Robot navigation
- Plant placement

### Phase 6 - Learning

Goal: Robot learns the preferences of the individual plant
- Observe
- Select location/action
- Move
- Measure environmental conditions
- Observe plant response
- Update plant model
- Select next action

### Phase 7 - Potential Enhancements

Goal: Robot is enhanced with whatever the developers see fit
- Plant avatar
- Plant watering system
- To be continued...
