import json
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class CrisisManagerBot:
    def __init__(self):
        self.crisis_plan = self.load_crisis_plan()

    def load_crisis_plan(self, file_path='crisis_management_plan.json'):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_crisis_plan(self, file_path='crisis_management_plan.json'):
        with open(file_path, 'w') as file:
            json.dump(self.crisis_plan, file)

    def handle_crisis_management(self):
        print("Welcome to Crisis Management. How can I assist you?")
        user_input = input("You: ")
        if "create" in user_input.lower():
            self.create_crisis_plan()
        elif "update" in user_input.lower():
            self.update_crisis_plan()
        elif "review" in user_input.lower():
            self.review_crisis_plan()
        elif "guide" in user_input.lower():
            self.guide_through_crisis_plan()
        else:
            self.handle_free_form_discussion(user_input)

    def create_crisis_plan(self):
        print("Let's create your Crisis Management Plan.")
        self.crisis_plan = {
            "Warning Signs": input("Enter your warning signs: "),
            "Coping Strategies": input("Enter your coping strategies: "),
            "Contacts": input("Enter your emergency contacts: "),
            "Environment Safety": input("Enter your plan for making your environment safe: ")
        }
        self.save_crisis_plan()
        print("Crisis Management Plan created successfully.")

    def update_crisis_plan(self):
        if not self.crisis_plan:
            print("No existing crisis management plan found. Let's create one first.")
            self.create_crisis_plan()
            return
        
        print("Updating your Crisis Management Plan.")
        for key in self.crisis_plan:
            new_value = input(f"Enter new value for {key} (leave blank to keep current value): ")
            if new_value:
                self.crisis_plan[key] = new_value
        self.save_crisis_plan()
        print("Crisis Management Plan updated successfully.")

    def review_crisis_plan(self):
        if not self.crisis_plan:
            print("No existing crisis management plan found. Let's create one first.")
            self.create_crisis_plan()
            return
        
        print("Reviewing your Crisis Management Plan.")
        for key, value in self.crisis_plan.items():
            print(f"{key}: {value}")

    def guide_through_crisis_plan(self):
        if not self.crisis_plan:
            print("No existing crisis management plan found. Let's create one first.")
            self.create_crisis_plan()
            return
        
        print("Guiding you through your Crisis Management Plan.")
        for key, value in self.crisis_plan.items():
            print(f"{key}: {value}")
            input("Press Enter to continue to the next step...")

    def handle_free_form_discussion(self, user_input):
        response = self.get_gpt4_response(user_input)
        print(f"DeeBoT: {response}")
        self.detect_and_redirect(user_input)

    def get_gpt4_response(self, user_input):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"You are DeeBoT, a DBT crisis management virtual assistant. The user says: '{user_input}'. Provide an appropriate response adhering to DBT standards.",
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def detect_and_redirect(self, user_input):
        if "create" in user_input.lower():
            print("Let's create your Crisis Management Plan.")
            self.create_crisis_plan()
        elif "update" in user_input.lower():
            print("Let's update your Crisis Management Plan.")
            self.update_crisis_plan()
        elif "review" in user_input.lower():
            print("Reviewing your Crisis Management Plan.")
            self.review_crisis_plan()
        elif "guide" in user_input.lower():
            print("Guiding you through your Crisis Management Plan.")
            self.guide_through_crisis_plan()
        else:
            print("How else can I assist you today?")
