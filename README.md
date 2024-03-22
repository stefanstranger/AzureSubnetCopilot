# Azure Virtual Network Subnet IP Range Solution

This solution is a Python Flask web application that calculates and displays the Azure Virtual Network IP range, existing subnets, and suitable IP range. This solution is designed to help you manage your Azure Virtual Network Subnet IP addresses in Azure Virtual Network. It provides a way to view your existing subnets and find a suitable IP range for new subnets based on your required number of IP addresses.

## How it works

The application takes input from the user, performs calculations, and displays the results in a web page or returns a json response.

The main components of the application are:

- `index.py`: This is the main Python script that runs the Flask application. It contains the routes and logic for calculating the IP ranges.

- `result.html`: This is the HTML template that displays the results. It uses Jinja2 templating to insert the results into the HTML.

- `styles.css`: This is the CSS file that styles the html pages.

- `error.html`: This is the HTML template that displays an error message if there is an issue with the input or calculation.

- `about.html`: This is the HTML template that provides information about the application and its purpose.

## How to run locally

### Clone Github Repository

To clone a GitHub repository on a local Windows machine, follow these steps:

1. Open a command prompt or PowerShell window.

2. Navigate to the directory where you want to clone the repository. You can use the cd command to change directories. For example, if you want to clone the repository into a directory called my_project, you would use the following command:

```PowerShell
cd C:\path\to\my_project
```

3. Once you are in the desired directory, use the git clone command followed by the URL of the GitHub repository. For example, if the repository URL is [https://github.com/stefanstranger/AzureSubnetCopilot.git](https://github.com/stefanstranger/AzureSubnetCopilot.git), you would use the following command:

```PowerShell
git clone https://github.com/stefanstranger/AzureSubnetCopilot.git
```

This will create a local copy of the repository in the current directory.

4. After the cloning process is complete, you can navigate into the cloned repository directory using the cd command. For example:

```PowerShell
cd repository
```

Now you can work with the files in the repository on your local machine.


### Install and configure Python environment

To run Python on a Windows system, you need to install Python and set up a Python environment. Here's how you can do it:

1. Install Python: Download the latest version of Python from the [official Python website](https://www.python.org/downloads/windows/). Run the installer, and make sure to check the box that says "Add Python to PATH" before you click "Install Now". This will make it easier to run Python from the command line.

2. Check the Python installation: Open a new command prompt window (you can do this by typing cmd into the search bar and hitting Enter), and type python --version. You should see the version of Python that you installed. If you see an error message, Python may not have been installed correctly.

3. Set up a Python environment: It's a good practice to create a separate Python environment for each project. This way, the dependencies of different projects won't interfere with each other. You can create a Python environment using the venv module that comes with Python. Here's how you can do it:

- Navigate to the directory where you have cloned the Git Repository.

- From within PowerShell host, create the environment by typing python3 -m venv env. This creates a new environment in a directory called env.

```PowerShell
python3 -m venv env
```

- Activate the environment by typing .\env\Scripts\activate. Your command prompt should now show (env) at the beginning of the line, indicating that the environment is active.
  
```PowerShell
.\env\Scripts\Activate.ps1
```

4. Install packages: With the environment active, you can install the required Python packages. In your case, you would type:

```PowerShell
pip install flask
pip install netaddr
pip install pandas
```

These commands install the Flask, netaddr, and pandas packages in the environment.

5. Run the application: With the packages installed, you can now run the application. Navigate to the .\api folder that contains the index.py file.

Then, run the index.py script:

```PowerShell
python3 .\index.py
```
Open a browser with the following url: http://127.0.0.1:5000

Remember to deactivate the environment when you're done working on the project. You can do this by typing deactivate in the command prompt.

## Online version

This solution is also available online at the following address: [https://azure-subnet-copilot.vercel.app/](https://azure-subnet-copilot.vercel.app/)