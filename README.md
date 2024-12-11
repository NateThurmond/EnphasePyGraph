-- Initial
python3 -m venv venv
-- Everytime
source venv/bin/activate
pip install -r requirements.txt
-- In pyenv
deactivate
-- Useful during dev after adding new packages
pip freeze > requirements.txt
