@echo off
REM Define project directory
set "projectDir=C:\Users\micha\Bot\voice"

REM Change to project directory
cd /d "%projectDir%"

REM Set environment variables
set "AZURE_OPENAI_API_KEY=your_openai_api_key"
set "AZURE_OPENAI_ENDPOINT=your_openai_endpoint"

REM Ensure the .env file exists and contains the necessary variables
(
echo AZURE_OPENAI_API_KEY=%AZURE_OPENAI_API_KEY%
echo AZURE_OPENAI_ENDPOINT=%AZURE_OPENAI_ENDPOINT%
) > .env

REM Create requirements.txt file
(
echo flask
echo openai
echo python-dotenv
) > requirements.txt

REM Install necessary Python packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Run the Flask application
python app.py
