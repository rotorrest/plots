
# Test 2 Shimoku Sales Data Analysis

This Python script is intended for demonstrating the options that Shimoku SDK has to integrate multiple plots per dashboard. The analysis results are plotted on the Shimoku board.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Before you can run the script, you need to have Python and the following Python libraries installed:

-   shimoku_api_python
-   python-dotenv
-   pandas

You can install these packages using pip:
```
pip install -r requirements.txt
```
We recommend the use of virtual environments.

### Installing

Clone the GitHub repository:

```bash
git clone https://github.com/<Your_GitHub_Username>/Your_Project_Name` 
```
Navigate to the project directory:

```bash
cd Your_Project_Name
```
### Running the Script

Before you can run the script, you need to set up the following environment variables:

-   `SHIMOKU_TOKEN`: your Shimoku API token
-   `UNIVERSE_ID`: your Universe ID in Shimoku
-   `WORKSPACE_ID`: your Workspace ID in Shimoku

You can set these variables in a `.env` file in the project root:

```makefile
SHIMOKU_TOKEN=<Your_Shimoku_API_Token>
UNIVERSE_ID=<Your_Universe_ID>
WORKSPACE_ID=<Your_Workspace_ID>` 
```
Then, you can run the script with the following command:

```Bash
python3 main.py
```
The script will generate dummy sales data, calculate various statistics, and plot them on the Shimoku board.

