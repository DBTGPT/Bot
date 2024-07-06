import json
import os
import csv
import openai
from evaluation.skill_presence_evaluation import SkillPresenceEvaluation
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class SkillsTrainerBot:
    def __init__(self):
        self.dbt_skills = self.load_dbt_skills('data/dbt_skills_ref.csv')
        self.provided_skills = self.load_provided_skills()
        self.handouts = self.load_handouts()
        self.worksheets = self.load_worksheets()
        self.progress = self.load_progress()

    def load_dbt_skills(self, file_path):
        dbt_skills = {}
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = row['module_category']
                skill = row['skill_name']
                if category not in dbt_skills:
                    dbt_skills[category] = []
                dbt_skills[category].append(skill)
        return dbt_skills

    def load_provided_skills(self, file_path='provided_skills.json'):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return {category: [] for category in self.dbt_skills.keys()}

    def save_provided_skills(self, file_path='provided_skills.json'):
        with open(file_path, 'w') as file:
            json.dump(self.provided_skills, file)

    def load_handouts(self):
        return {
            "General Skills": [
                "Goals of Skills Training", "Options for Solving Any Problem", "Overview—Introduction to Skills Training",
                "Guidelines for Skills Training", "Skills Training Assumptions", "Biosocial Theory", "Overview—Analyzing Behavior",
                "Chain Analysis", "Chain Analysis, Step by Step", "Missing-Links Analysis"
            ],
            "Mindfulness Skills": [
                "Goals of Mindfulness Practice", "Mindfulness Definitions", "Overview—Core Mindfulness Skills", "Wise Mind—States of Mind",
                "Ideas for Practicing Wise Mind", "Taking Hold of Your Mind—“What” Skills", "Ideas for Practicing Observing",
                "Ideas for Practicing Describing", "Ideas for Practicing Participating", "Taking Hold of Your Mind—“How” Skills",
                "Ideas for Practicing Nonjudgmentalness", "Ideas for Practicing One-Mindfulness", "Ideas for Practicing Effectiveness",
                "Overview—Other Perspectives on Mindfulness", "Goals of Mindfulness Practice—A Spiritual Perspective",
                "Wise Mind from a Spiritual Perspective", "Practicing Loving Kindness to Increase Love and Compassion",
                "Skillful Means—Balancing Doing Mind and Being Mind", "Ideas for Practicing Balancing Doing Mind and Being Mind",
                "Walking the Middle Path—Finding the Synthesis Between Opposites"
            ],
            "Interpersonal Effectiveness Skills": [
                "Goals of Interpersonal Effectiveness", "Factors in the Way of Interpersonal Effectiveness", "Myths in the Way of Interpersonal Effectiveness",
                "Overview—Obtaining Objectives Skillfully", "Clarifying Goals in Interpersonal Situations", "Guidelines for Objectives Effectiveness—Getting What You Want (DEAR MAN)",
                "Applying DEAR MAN Skills to a Difficult Current Interaction", "Guidelines for Relationship Effectiveness—Keeping the Relationship (GIVE)",
                "Expanding the V in GIVE—Levels of Validation", "Guidelines for Self-Respect Effectiveness—Keeping Respect for Yourself (FAST)",
                "Evaluating Options for Whether or How Intensely to Ask for Something or Say No", "Troubleshooting—When What You Are Doing Isn’t Working",
                "Overview—Building Relationships and Ending Destructive Ones", "Finding and Getting People to Like You", "Identifying Skills to Find People and Get Them to Like You",
                "Mindfulness of Others", "Identifying Mindfulness of Others", "Ending Relationships", "Identifying How to End Relationships",
                "Overview—Walking the Middle Path", "Dialectics", "How to Think and Act Dialectically", "Examples of Opposite Sides That Can Both Be True",
                "Important Opposites to Balance", "Identifying Dialectics", "Validation", "A “How To” Guide to Validation", "Identifying Validation",
                "Recovering from Invalidation", "Identifying Self-Validation", "Strategies for Increasing the Probability of Behaviors You Want",
                "Strategies for Decreasing or Stopping Unwanted Behaviors", "Tips for Using Behavior Change Strategies Effectively", "Identifying Effective Behavior Change Strategies"
            ],
            "Emotion Regulation Skills": [
                "Goals of Emotion Regulation", "Overview—Understanding and Naming Emotions", "What Emotions Do for You",
                "What Makes It Hard to Regulate Your Emotions", "Myths About Emotions", "Model for Describing Emotions", "Ways to Describe Emotions",
                "Overview—Changing Emotional Responses", "Check the Facts", "Examples of Emotions That Fit the Facts", "Opposite Action and Problem Solving—Deciding Which to Use",
                "Opposite Action", "Figuring Out Opposite Actions", "Problem Solving", "Reviewing Opposite Action and Problem Solving",
                "Overview—Reducing Vulnerability to Emotion Mind: Building a Life Worth Living", "Accumulating Positive Emotions—Short Term", "Pleasant Events List",
                "Accumulating Positive Emotions—Long Term", "Values and Priorities List", "Build Mastery and Cope Ahead", "Taking Care of Your Mind by Taking Care of Your Body",
                "Nightmare Protocol, Step by Step—When Nightmares Keep You from Sleeping", "Sleep Hygiene Protocol", "Overview—Managing Really Difficult Emotions",
                "Mindfulness of Current Emotions—Letting Go of Emotional Suffering", "Managing Extreme Emotions", "Troubleshooting Emotion Regulation Skills—When What You Are Doing Isn’t Working",
                "Review of Skills for Emotion Regulation"
            ],
            "Distress Tolerance Skills": [
                "Goals of Distress Tolerance", "Overview—Crisis Survival Skills", "When to Use Crisis Survival Skills", "STOP Skill", "Pros and Cons",
                "TIP Skills—Changing Your Body Chemistry", "Using Cold Water, Step by Step", "Paired Muscle Relaxation, Step by Step",
                "Effective Rethinking and Paired Relaxation, Step by Step", "Distracting", "Self-Soothing", "Body Scan Meditation Step by Step",
                "Improving the Moment", "Sensory Awareness, Step by Step", "Overview—Reality Acceptance Skills", "Radical Acceptance",
                "Radical Acceptance—Factors That Interfere", "Practicing Radical Acceptance Step by Step", "Turning the Mind", "Willingness",
                "Half-Smiling and Willing Hands", "Practicing Half-Smiling and Willing Hands", "Mindfulness of Current Thoughts", "Practicing Mindfulness of Thoughts",
                "Overview—When the Crisis Is Addiction", "Common Addictions", "Dialectical Abstinence", "Planning for Dialectical Abstinence",
                "Clear Mind", "Behavior Patterns Characteristic of Addict Mind and of Clean Mind", "Community Reinforcement", "Burning Bridges and Building New Ones",
                "Alternate Rebellion and Adaptive Denial"
            ]
        }

    def load_worksheets(self):
        return {
            "General Skills": [
                "Pros and Cons of Using Skills", "Chain Analysis of Problem Behavior", "Missing-Links Analysis"
            ],
            "Mindfulness Skills": [
                "Pros and Cons of Practicing Mindfulness", "Mindfulness Core Skills Practice", "Wise Mind Practice",
                "Mindfulness “What” Skills—Observing, Describing, Participating", "Mindfulness “How” Skills—Nonjudgmentalness, One-Mindfulness, Effectiveness",
                "Loving Kindness", "Balancing Being Mind with Doing Mind", "Mindfulness of Pleasant Events Calendar", "Mindfulness of Unpleasant Events Calendar",
                "Walking the Middle Path to Wise Mind"
            ],
            "Interpersonal Effectiveness Skills": [
                "Pros and Cons of Using Interpersonal Effectiveness Skills", "Challenging Myths in the Way of Obtaining Objectives",
                "Clarifying Priorities in Interpersonal Situations", "Writing Out Interpersonal Effectiveness Scripts", 
                "Tracking Interpersonal Effectiveness Skills Use", "The DIME Game—Figuring Out How Strongly to Ask or Say No",
                "Troubleshooting Interpersonal Effectiveness Skills", "Finding and Getting People to Like You", "Mindfulness of Others", "Ending Relationships                 "Finding and Getting People to Like You", "Mindfulness of Others", "Ending Relationships",
                "Practicing Dialectics", "Dialectics Checklist", "Noticing When You’re Not Dialectical", "Validating Others",
                "Self-Validation and Self-Respect", "Changing Behavior with Reinforcement", "Changing Behavior by Extinguishing or Punishing It"
            ],
            "Emotion Regulation Skills": [
                "Pros and Cons of Changing Emotions", "Figuring Out What My Emotions Are Doing for Me", "Emotion Diary",
                "Myths About Emotions", "Observing and Describing Emotions", "Check the Facts", "Figuring Out How to Change Unwanted Emotions",
                "Opposite Action to Change Emotions", "Problem Solving to Change Emotions", "Steps for Reducing Vulnerability to Emotion Mind",
                "Pleasant Events Diary", "Getting from Values to Specific Action Steps", "Diary of Daily Actions on Values and Priorities",
                "Build Mastery and Cope Ahead", "Putting ABC Skills Together Day by Day", "Practicing PLEASE Skills", "Target Nightmare Experience Forms",
                "Sleep Hygiene Practice Sheet", "Mindfulness of Current Emotions", "Troubleshooting Emotion Regulation Skills"
            ],
            "Distress Tolerance Skills": [
                "Crisis Survival Skills", "Practicing the STOP Skill", "Pros and Cons of Acting on Crisis Urges", "Changing Body Chemistry with TIP Skills",
                "Distracting with Wise Mind ACCEPTS", "Self-Soothing", "Improve the Moment", "Reality Acceptance Skills", "Practicing Radical Acceptance",
                "Turning the Mind, Willingness, Willfulness", "Half-Smiling and Willing Hands", "Mindfulness of Current Thoughts",
                "Skills When the Crisis Is Addiction", "Planning for Dialectical Abstinence", "From Clean Mind to Clear Mind",
                "Reinforcing Nonaddictive Behaviors", "Burning Bridges and Building New Ones", "Practicing Alternate Rebellion and Adaptive Denial"
            ]
        }

    def load_progress(self, file_path='progress.json'):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return {category: {"handouts": [], "worksheets": []} for category in self.dbt_skills.keys()}

    def save_progress(self, file_path='progress.json'):
        with open(file_path, 'w') as file:
            json.dump(self.progress, file)

    def handle_skills_training(self):
        print("Welcome to Skills Training. How can I assist you?")
        user_input = input("You: ")
        if "review" in user_input.lower():
            self.review_skill_progress()
        elif "learn" in user_input.lower():
            self.present_handouts(user_input)
        elif "complete" in user_input.lower():
            self.administer_worksheets(user_input)
        else:
            print("I'm sorry, I didn't understand that. Please specify if you want to review your progress, learn a handout, or complete a worksheet.")
            self.handle_skills_training()

    def present_handouts(self, user_input):
        category = self.identify_category(user_input)
        if category:
            for handout in self.handouts[category]:
                if handout not in self.progress[category]["handouts"]:
                    print(f"Handout: {handout}")
                    self.progress[category]["handouts"].append(handout)
                    self.save_progress()
                    return
            print(f"You have completed all handouts for {category}.")
        else:
            print("Could not identify the category. Please specify the category of handouts you want to learn.")

    def administer_worksheets(self, user_input):
        category = self.identify_category(user_input)
        if category:
            for worksheet in self.worksheets[category]:
                if worksheet not in self.progress[category]["worksheets"]:
                    print(f"Worksheet: {worksheet}")
                    response = input("Please provide your response: ")
                    self.progress[category]["worksheets"].append({"worksheet": worksheet, "response": response})
                    self.save_progress()
                    return
            print(f"You have completed all worksheets for {category}.")
        else:
            print("Could not identify the category. Please specify the category of worksheets you want to complete.")

    def identify_category(self, user_input):
        if "general" in user_input.lower():
            return "General Skills"
        elif "mindfulness" in user_input.lower():
            return "Mindfulness Skills"
        elif "interpersonal" in user_input.lower():
            return "Interpersonal Effectiveness Skills"
        elif "emotion" in user_input.lower():
            return "Emotion Regulation Skills"
        elif "distress" in user_input.lower():
            return "Distress Tolerance Skills"
        else:
            return None

    def review_skill_progress(self):
        print("Reviewing skill progress:")
        for category, items in self.progress.items():
            print(f"\n{category} Handouts Completed: {', '.join(items['handouts']) if items['handouts'] else 'None'}")
            print(f"{category} Worksheets Completed: {', '.join([ws['worksheet'] for ws in items['worksheets']]) if items['worksheets'] else 'None'}")

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
            self.handle_skills_training()
        elif "crisis" in user_input.lower():
            print("It seems like you need help with crisis management.")
            # Assuming CrisisManagerBot is instantiated in a similar way
            CrisisManagerBot().handle_crisis_management()
        elif "diary" in user_input.lower():
            print("Let's work on your diary card.")
            # Assuming DiaryBot is instantiated in a similar way
            DiaryBot().handle_diary_card()
        elif "adherence" in user_input.lower():
            print("Let's check for DBT adherence.")
            # Assuming AdherenceBot is instantiated in a similar way
            AdherenceBot().handle_adherence_check()
        elif "review" in user_input.lower():
            print("Reviewing your skill progress.")
            self.review_skill_progress()
        else:
            print("How else can I assist you today?")

