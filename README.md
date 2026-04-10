# Sprint Planning Optimization Tool

A comprehensive solution for optimizing ticket assignment in agile development sprints using machine learning predictions and mathematical optimization.

## Overview

This project provides an end-to-end system for sprint planning that combines:
- **Machine Learning**: XGBoost regression model to predict ticket completion times
- **Optimization**: Gurobi-based mathematical programming for balanced workload distribution
- **Interactive Dashboard**: Streamlit web application for sprint planning and team management

## Project Structure

```
├── app.py                   # Streamlit web application
├── optimization.py          # Gurobi optimization model
├── EDA.ipynb                # Exploratory data analysis
├── model.ipynb              # Machine learning model training
├── analysis.ipynb           # Performance analysis and results
├── predictions.csv          # ML model predictions
├── jira_m2_accelerated.csv  # Original Jira ticket data
└── README.md                # Project documentation
```

## Prerequisites
- Python 3.8+
- Gurobi license (for optimization)
- Required packages: pandas, streamlit, xgboost, gurobipy, matplotlib, seaborn


## Machine Learning Model
- **Target**: Time to resolution (hours)
- **Performance**: R² score evaluation with train/test split
- **Output**: `predictions.csv` with completion time estimates

## Optimization Algorithm
- Capacity-constrained assignment problem
- Load balancing across team members
- Sprint duration and team capacity management

## Web Application

### Running The Interface
```bash
streamlit run app.py
```
