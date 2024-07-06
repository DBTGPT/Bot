import openai
import os
from skills_trainer_bot import SkillsTrainerBot
from crisis_manager_bot import CrisisManagerBot
from diary_bot import DiaryBot
from adherence_bot import AdherenceBot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class DBTTherapistBot:
    def __init__(self):
        self.skills_trainer = SkillsTrainerBot()
        self.crisis_manager = CrisisManagerBot()
        self.diary_bot = DiaryBot()
        self.adherence_bot = AdherenceBot()

    def introduce(self):
        print("Welcome to DBT Therapy. I am your DBT Therapist. How can I assist you today?")
        print("1. Skills Training")
        print("2. Crisis Management")
        print("3. Diary Card")
        print("4. Adherence Check")
        print("5. Review Skill Progress")

    def triage(self, user_input):
        if "skills" in user_input.lower():
            self.skills_trainer.handle_skills_training()
        elif "crisis" in user_input.lower():
            self.crisis_manager.handle_crisis_management()
        elif "diary" in user_input.lower():
            self.diary_bot.handle_diary_card()
        elif "adherence" in user_input.lower():
            self.adherence_bot.handle_adherence_check()
        elif "review" in user_input.lower():
            self.skills_trainer.review_skill_progress()
        else:
            self.handle_free_form_discussion(user_input)

    def handle_free_form_discussion(self, user_input):
        response = self.get_gpt4_response(user_input)
        print(f"DeeBoT: {response}")
        self.detect_and_redirect(user_input)

    def get_gpt4_response(self, user_input):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"You are DeeBoT, a DBT skills training virtual assistant. The user says: '{user_input}'. Provide an appropriate response adhering to DBT standards.",
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def detect_and_redirect(self, user_input):
        if "skills" in user_input.lower():
            print("It seems like you want to learn more about skills training.")
            self.skills_trainer.handle_skills_training()
        elif "crisis" in user_input.lower():
            print("It seems like you need help with crisis management.")
            self.crisis_manager.handle_crisis_management()
        elif "diary" in user_input.lower():
            print("Let's work on your diary card.")
            self.diary_bot.handle_diary_card()
        elif "adherence" in user_input.lower():
            print("Let's check for DBT adherence.")
            self.adherence_bot.handle_adherence_check()
        elif "review" in user_input.lower():
            print("Reviewing your skill progress.")
            self.skills_trainer.review_skill_progress()
        else:
            print("How else can I assist you today?")

