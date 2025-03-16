# Use whichever Python version you prefer
FROM python:3.10-slim

# Make sure basic utilities are installed if your code uses them.
# This is an example list; adapt to your needs:
RUN apt-get update && apt-get install -y \
    coreutils \
    grep \
    # (any other packages your code needs)
    && rm -rf /var/lib/apt/lists/*

# Set a working directory inside the container
WORKDIR /agentic_ai

# Copy only the requirements file (if exists)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local folder into the container
COPY . . 

# Run your script
CMD ["python", "src/main.py", "admin"]