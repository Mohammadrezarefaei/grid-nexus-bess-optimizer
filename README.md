# Grid-Nexus BESS Optimizer

Welcome to the Grid-Nexus Battery Energy Storage System (BESS) Optimizer. This is a web application built with Streamlit that helps you find the most profitable charging and discharging strategy for a battery system based on dynamic electricity prices.

By using linear programming, the app calculates exactly when the battery should buy power from the grid and when it should sell it back to maximize overall profit. 

## Key Features

* Interactive web interface to easily adjust battery parameters.
* Customizable inputs for battery capacity, maximum power, round-trip efficiency, and initial State of Charge.
* Fast linear optimization powered by the PuLP library.
* Beautiful and interactive charts created with Plotly to visualize the electricity price, net battery power, and State of Charge over time.
* Detailed data table showing the exact optimization results for each hour.

## How It Works

The optimizer looks at a given timeline of electricity prices. It then creates a mathematical model to maximize the total revenue (money earned from discharging) minus the total cost (money spent on charging). The algorithm respects all physical limits of the battery, including its maximum power capacity and energy losses during the charge cycle.

## Installation and Local Setup

If you want to run this project on your own computer, follow these simple steps:

1. Clone this repository to your local machine.
2. Open your terminal or command prompt in the project folder.
3. Install the required Python packages by running:
   `pip install -r requirements.txt`
4. Start the application by running:
   `streamlit run app.py`

Your default web browser will open automatically and display the app.

## Technologies Used

* Python
* Streamlit for the frontend application
* PuLP for linear programming and optimization
* Plotly for interactive data visualization
* Pandas and NumPy for data handling

## Future Improvements

We plan to add more features soon, such as the ability to
