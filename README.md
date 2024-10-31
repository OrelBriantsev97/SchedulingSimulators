# CPU-Scheduling-Algorithms-Simulators

This repo contains simulators for CPU scheduling algorithms, adapted from university project I've developed to study and compare process scheduling techniques.

## CPU Scheduling Simulators

This tool provides an accessible way to experiment with and analyze the performance of common CPU scheduling algorithms, including Round Robin (RR), Shortest Job First (SJF), and Priority Scheduling.

## Environment

This application is developed to run on a Linux environment using Windows Subsystem for Linux (WSL) and requires VCXsrv to enable graphical support for the Tkinter GUI. Ensure VCXsrv is installed and running to support the GUI when launching the application through WSL.

### Features:

**Algorithm Simulations**: Simulate Round Robin, Shortest Job First, and Priority Scheduling algorithms.
**Interactive GUI**: Allows selection of key parameters like process count, maximum burst time, and maximum priority (Priority Scheduling).
**Performance Metrics**: Calculate and display metrics including CPU utilization, memory usage, waiting time, turnaround time, response time, and context switching.
**Adjustable Parameters**: Easily set number of processes, maximum burst time, and (for Priority Scheduling) a priority range.
**Real-Time Metrics**: Track CPU and memory utilization, calculate fairness, and record process timing metrics.


## Algorithm Details and Usage

Each simulator is implemented with a specific purpose:

### Round Robin (RR) Simulator

This simulator applies the Round Robin algorithm with an adjustable time quantum, helping visualize fairness, CPU utilization, and response times.

### Shortest Job First (SJF) Simulator

Implements the SJF algorithm, prioritizing tasks with the shortest burst time to improve throughput and response efficiency.

### Priority Scheduling Simulator

Supports both preemptive and non-preemptive priority scheduling, scheduling tasks based on priority values.
