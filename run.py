from prompt.user_prompt import UserPrompt
import os
import sys

if __name__ == "__main__":
    #Check if there is a dev argument
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        os.environ["ENVIRONMENT"] = "development"
    else:
        os.environ["ENVIRONMENT"] = "production"
    UserPrompt().main_menu()
    