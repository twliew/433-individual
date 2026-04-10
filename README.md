# 433-individual: Sprint Planning Optimization Tool

A comprehensive solution for optimizing ticket assignment in agile development sprints using machine learning predictions and mathematical optimization.

## Overview

This project provides an end-to-end system for sprint planning that combines:
- **Machine Learning**: XGBoost regression model to predict ticket completion times
- **Optimization**: Gurobi-based mathematical programming for balanced workload distribution
- **Interactive Dashboard**: Streamlit web application for sprint planning and team management

## Features

### 🎯 Core Functionality
- **Predictive Modeling**: ML-powered estimation of ticket completion times
- **Workload Optimization**: Balanced assignment of tickets to developers
- **Sprint Planning**: Interactive dashboard for managing sprints and team capacity
- **Performance Analysis**: Comparison of optimized vs. original workload distributions

### 📊 Data Analysis
- Exploratory data analysis of Jira ticket data
- Feature engineering and data preprocessing
- Model evaluation and performance metrics

### 🚀 Optimization
- Capacity-constrained assignment problem
- Load balancing across team members
- Sprint duration and team capacity management

## Project Structure

```
├── app.py                 # Streamlit web application
├── optimization.py        # Gurobi optimization model
├── EDA.ipynb             # Exploratory data analysis
├── model.ipynb           # Machine learning model training
├── analysis.ipynb        # Performance analysis and results
├── predictions.csv       # ML model predictions
├── jira_m2_accelerated.csv # Original Jira ticket data
└── README.md            # Project documentation
```

## Data

The project uses Jira ticket data with the following key features:
- **Ticket Information**: Issue key, type, priority, status, component
- **Time Metrics**: Creation/update dates, resolution time in hours
- **Relationships**: Parent epics, stories, subtasks
- **Team Data**: Assignee/reporter IDs, watchers, comments
- **Content**: Problem statements, descriptions, root causes

## Machine Learning Model

### XGBoost Regressor
- **Target**: Time to resolution (hours)
- **Features**: Priority, issue type, component, sprint, team metrics
- **Performance**: R² score evaluation with train/test split
- **Output**: `predictions.csv` with completion time estimates

### Model Training Process
1. Data cleaning and preprocessing
2. Feature encoding (ordinal and label encoding)
3. Train/test split (80/20)
4. Hyperparameter tuning
5. Model evaluation and prediction generation

## Optimization Algorithm

### Mathematical Programming Model
- **Objective**: Minimize maximum developer workload (load balancing)
- **Constraints**:
  - Each ticket assigned to exactly one developer
  - Developer capacity limits (hours per week × sprint duration)
- **Solver**: Gurobi optimization engine
- **Variables**: Binary assignment variables, maximum load variable

### Key Features
- Capacity-aware assignment
- Load balancing across team members
- Sprint duration flexibility
- Team capacity management

## Web Application

### Streamlit Dashboard
- **Sprint Management**: Configure sprint duration and number
- **Team Capacity**: Add/remove developers, set weekly hours
- **Ticket Selection**: Interactive backlog with filtering
- **Optimization**: One-click workload optimization
- **Progress Tracking**: Assignment and completion tracking

### User Interface
- Three-column layout: Backlog, Assignments, Completed
- Real-time capacity checking
- Sprint completion workflow
- Developer workload visualization

## Installation & Setup

### Prerequisites
- Python 3.8+
- Gurobi license (for optimization)
- Required packages: pandas, streamlit, xgboost, gurobipy, matplotlib, seaborn

### Installation
```bash
# Clone repository
git clone <repository-url>
cd 433-individual

# Install dependencies
pip install -r requirements.txt

# Set up virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

## Usage

### 1. Data Preparation
- Run `EDA.ipynb` for data exploration
- Execute `model.ipynb` to train ML model and generate predictions
- Review `analysis.ipynb` for performance comparison

### 2. Sprint Planning
1. Launch the Streamlit app
2. Configure sprint duration and team members
3. Select tickets from the backlog
4. Click "Optimize Selected" for balanced assignment
5. Review assignments and complete sprint

### 3. Optimization Analysis
- Compare optimized vs. original workload distributions
- Analyze team utilization and capacity
- Evaluate prediction accuracy

## Results & Analysis

The optimization system demonstrates significant improvements in:
- **Workload Balance**: Reduced variance in developer workloads
- **Capacity Utilization**: Better alignment with team capacity
- **Predictive Accuracy**: ML model performance metrics
- **Planning Efficiency**: Streamlined sprint planning process

## Technologies Used

- **Machine Learning**: XGBoost, scikit-learn
- **Optimization**: Gurobi
- **Web Framework**: Streamlit
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Development**: Python, Jupyter Notebooks

## Future Enhancements

- [ ] Real-time Jira integration
- [ ] Advanced ML models (neural networks, ensemble methods)
- [ ] Multi-objective optimization (quality, deadlines)
- [ ] Historical performance tracking
- [ ] Team skill-based assignment
- [ ] Risk assessment and mitigation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

## License

[Specify license if applicable]

## Contact

[Add contact information or project maintainer details]