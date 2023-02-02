## CHT Hierarchy Generator

Simple python script to generate a custom address hierarchy for Community Health Toolkit

#### Usage

Step 1: Create a location configuration `json` file called locations.json with the address hierarchy and structre in the way you need to. You can take inspiration from the example above.

Step 2: Set the credentials (Username & Password) in the client.py file and URL to the CHT instance in main.py
> Note: This will later be moved to an env file, for easier configuration

Step 3: Run the migration command
```bash
# Requires python3.9 or higher

# For Linux Users
python3 main.py

# For Windows Users
python main.py
```
