# Azure VNet IP Range Solution

This solution is a Flask web application that calculates and displays the Azure VNet IP range, existing subnets, and suitable IP range.

## How it works

The application takes input from the user, performs calculations, and displays the results in a web page. The results are displayed in a human-readable format.

The main components of the application are:

- `index.py`: This is the main Python script that runs the Flask application. It contains the routes and logic for calculating the IP ranges.

- `result.html`: This is the HTML template that displays the results. It uses Jinja2 templating to insert the results into the HTML.

- `styles.css`: This is the CSS file that styles the `result.html` template.

## How to run

To run the application, first install the required Python packages:

```bash
pip install flask
pip install netaddr
pip install pandas
```

Then, run the index.py script:

```bash
python index.py
```