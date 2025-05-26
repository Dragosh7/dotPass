from utils.setup import profile_exists
from ui.interface import launch_app
from ui.create_profile_page import CreateProfilePage

if __name__ == "__main__":
    if profile_exists():
        launch_app()
    else:
        CreateProfilePage()