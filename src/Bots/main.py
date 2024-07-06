from dbt_therapist_bot import DBTTherapistBot

def main():
    dbt_therapist = DBTTherapistBot()
    dbt_therapist.introduce()
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Thank you for using DBT Therapy Bot. Goodbye!")
            break
        
        dbt_therapist.triage(user_input)

if __name__ == "__main__":
    main()