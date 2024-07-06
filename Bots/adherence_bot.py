import openai
from dotenv import load_dotenv
import os
from evaluation.adherence_evaluation import evaluate_adherence
from evaluation.skill_presence_evaluation import SkillPresenceEvaluation

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class AdherenceBot:
    def __init__(self):
        self.adherence_evaluator = evaluate_adherence
        self.skill_evaluator = SkillPresenceEvaluation()

    def filter_response(self, user_input, bot_response):
        adherence_feedback = self.adherence_evaluator(bot_response)
        if adherence_feedback['adherent']:
            return bot_response
        else:
            return self.generate_adherent_response(user_input, adherence_feedback)

    def generate_adherent_response(self, user_input, feedback):
        prompt = f"The user says: '{user_input}'. The bot's response was found non-adherent due to: {feedback['issues']}. Provide a response adhering to DBT AC-I standards."
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def handle_adherence_check(self, user_input, bot_response):
        print("Performing adherence check...")
        adherence_feedback = self.adherence_evaluator(bot_response)
        print(f"Adherence Check: {adherence_feedback}")
        if adherence_feedback['adherent']:
            print("The response is adherent.")
        else:
            print("The response is not adherent. Generating a new response...")
            new_response = self.generate_adherent_response(user_input, adherence_feedback)
            print(f"New Response: {new_response}")

    def handle_free_form_discussion(self, user_input):
        response = self.get_gpt4_response(user_input)
        filtered_response = self.filter_response(user_input, response)
        print(f"DeeBoT: {filtered_response}")

    def get_gpt4_response(self, user_input):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"You are DeeBoT, a DBT adherence virtual assistant. The user says: '{user_input}'. Provide an appropriate response adhering to DBT AC-I standards.",
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def detect_and_redirect(self, user_input):
        if "check" in user_input.lower():
            print("Performing adherence check.")
            self.handle_adherence_check(user_input)
        else:
            print("How else can I assist you today?")
