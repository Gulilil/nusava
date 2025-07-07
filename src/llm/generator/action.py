import numpy as np
import random
from hmmlearn.hmm import CategoricalHMM
from utils.constant import HMM_HIDDEN_STATES, HMM_OBSERVATION_LIST
from datetime import datetime, timezone, timedelta
from typing import Tuple

class ActionGenerator:
    """
    Component that generates which action to do for the agent.
    Possible actions: 'like', 'follow', 'comment', 'none'
    """

    def __init__(self):
        """
        Instantiate action generator.
        """
        self.hidden_states = HMM_HIDDEN_STATES
        self.observation_symbols = HMM_OBSERVATION_LIST

    
    def observe_statistics(self, statistics: dict) -> list:
        """
        Function to observe statistics.
        Returns a list of observations based on the statistics.
        Statistics -> "new_comments, new_followers, new_likes"
        """
        
        observations = []
        # Engagement based
        if (statistics[0] and isinstance(statistics[0], int)):
          observations.extend(["new_comment" for _ in range(statistics[0])])
        if (statistics[1] and isinstance(statistics[1], int)):
          observations.extend(["new_follower" for _ in range(statistics[1])])
        if (statistics[2] and isinstance(statistics[2], int)):
          observations.extend(["post_liked" for _ in range(statistics[2])])

        # Shuffle the observation
        random.shuffle(observations)

        # Time based
        current_time = datetime.now(timezone.utc) + timedelta(hours=7)
        current_hour = current_time.hour
        if 5 <= current_hour < 12:
            observations.insert(0, "morning_time")
        elif 12 <= current_hour < 18:
            observations.insert(0, "afternoon_time")
        else:
            observations.insert(0, "night_time")

        return observations


    def decide_action(self, observations: list, iteration: int) -> Tuple[str, str]:
        """
        Function to decide action.
        Returns one of: 'like', 'follow', 'comment', None

        The more iteration, the more likely to be in idle state
        """
        try:
          # Map observations to integers
          obs_to_idx = {obs: idx for idx, obs in enumerate(self.observation_symbols)}
          obs_idx = [obs_to_idx[o] for o in observations]
          obs_sequence = np.array(obs_idx).reshape(-1, 1)

          # Build and train the HMM
          model = CategoricalHMM(n_components=len(self.hidden_states), n_iter=100, random_state=42)
          # Define starting probability
          model.startprob_ = np.array([0.40, 0.40, 0.2])

          # Increase idle probability with iterations
          idle_addition_prob = (0.1 * iteration)  

          # Define transition matrix
          model.transmat_ = np.array([
              [(0.9 - idle_addition_prob) * 5/9 , (0.9 - idle_addition_prob) * 4/9  , 0.1 + idle_addition_prob],  # growth
              [(0.9 - idle_addition_prob) * 3/9 , (0.9 - idle_addition_prob) * 6/9  , 0.1 + idle_addition_prob],  # engagement
              [(1.0 - idle_addition_prob) / 2   , (1.0 - idle_addition_prob) / 2    , 0.0 + idle_addition_prob]   # idle
          ])
          # Define emission probability
          model.emissionprob_ = np.array([
                # new_com, new_fol, liked, morning, afternoon, night
                [0.20,    0.30,    0.20,    0.12,    0.10,    0.08],   # growth
                [0.30,    0.20,    0.20,    0.08,    0.12,    0.10],   # engagement
                [0.20,    0.20,    0.30,    0.10,    0.10,    0.10],    # idle
            ])


          # Predict hidden states from observation sequence
          state_sequence = model.predict(obs_sequence)
          state_sequence_str = [self.hidden_states[state] for state in state_sequence]
          print(f"[STATE SEQUENCE {iteration+1}] {state_sequence_str}")
          current_state = self.hidden_states[state_sequence[-1]]

          # Define simplified action policies
          state_action_map = {
              'growth': ['follow',  'like'],
              'engagement': ['comment', 'like'],
              'idle': ['like', None] 
          }
          possible_actions = state_action_map[current_state]
          chosen_action = random.choice(possible_actions)
          return chosen_action, current_state
        
        except Exception as e:
            print(f"Error in action generation: {e}")
            return None, None