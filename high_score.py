import json
import os

class HighScores:
    def __init__(self):
        self.scores = {
            'easy': 0,
            'medium': 0,
            'hard': 0
        }
        self.scores_file = 'high_scores.json'
        self.load_scores()

    def load_scores(self):
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    self.scores = json.load(f)
        except:
            pass

    def save_scores(self):
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f)
        except:
            pass

    def update_score(self, difficulty, score):
        # If new high score -> True
        if score > self.scores[difficulty]:
            self.scores[difficulty] = int(score)
            self.save_scores()
            return True
        return False

    def get_score(self, difficulty):
        return self.scores[difficulty]