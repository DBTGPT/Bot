import json
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class DiaryBot:
    def __init__(self):
        self.diary_entries = self.load_diary_entries()

    def load_diary_entries(self, file_path='diary_card_entries.json'):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_diary_entries(self, file_path='diary_card_entries.json'):
        with open(file_path, 'w') as file:
            json.dump(self.diary_entries, file)

    def handle_diary_card(self):
        print("Welcome to Diary Card Management. How can I assist you?")
        user_input = input("You: ")
        if "fill" in user_input.lower():
            self.fill_out_diary_card()
        elif "review" in user_input.lower():
            self.review_diary_card()
        elif "remind" in user_input.lower():
            self.set_diary_reminder()
        else:
            self.handle_free_form_discussion(user_input)

    def fill_out_diary_card(self):
        date = datetime.now().strftime("%Y-%m-%d")
        print(f"Filling out diary card for {date}.")
        diary_entry = {
            "Emotions": input("Enter your emotions today: "),
            "Behaviors": input("Enter your behaviors today: "),
            "Thoughts": input("Enter your thoughts today: "),
            "Skills Used": input("Enter the DBT skills you used today: ")
        }
        self.diary_entries[date] = diary_entry
        self.save_diary_entries()
        print("Diary card entry saved successfully.")

    def review_diary_card(self):
        date = input("Enter the date of the diary card you want to review (YYYY-MM-DD): ")
        if date in self.diary_entries:
            entry = self.diary_entries[date]
            print(f"Diary card for {date}:")
            for key, value in entry.items():
                print(f"{key}: {value}")
        else:
            print("No diary card entry found for that date.")

    def set_diary_reminder(self):
        print("Setting a reminder for filling out your diary card.")
        # Implement reminder functionality here (e.g., email, notification)

    def handle_free_form_discussion(self, user_input):
        response = self.get_gpt4_response(user_input)
        print(f"DeeBoT: {response}")
        self.detect_and_redirect(user_input)

    def get_gpt4_response(self, user_input):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"You are DeeBoT, a DBT diary card management virtual assistant. The user says: '{user_input}'. Provide an appropriate response adhering to DBT standards.",
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def detect_and_redirect(self, user_input):
        if "fill" in user_input.lower():
            print("Let's fill out your diary card.")
            self.fill_out_diary_card()
        elif "review" in user_input.lower():
            print("Reviewing your diary card.")
            self.review_diary_card()
        elif "remind" in user_input.lower():
            print("Setting a reminder for your diary card.")
            self.set_diary_reminder()
        else:
            print("How else can I assist you today?")

