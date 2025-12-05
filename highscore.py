import os
from config import HIGH_SCORE_FILE

def load_highscore():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write(str(score))

def update_highscore(score):
    current_high = load_highscore()
    if score > current_high:
        save_highscore(score)
        return True
    return False