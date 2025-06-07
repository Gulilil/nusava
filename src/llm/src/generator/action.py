import numpy as np
import random
from hmmlearn import hmm

class ActionGenerator:
    """
    Component that generates which action to do for the agent.
    Possible actions: 'like', 'follow', 'comment'
    """

    def __init__(self):
        """
        Instantiate action generator.
        """
        self.hidden_states = ['growth', 'engagement', 'support', 'idle']
        self.observation_symbols = ['high_inbox', 'new_follower', 'low_engagement', 'high_activity_time']

    def decide_action(self):
        """
        Function to decide action.
        Returns one of: 'like', 'follow', 'comment'
        """
        # Map observations to integers
        obs_to_idx = {obs: idx for idx, obs in enumerate(self.observation_symbols)}
        observations = [obs_to_idx[o] for o in ['new_follower', 'high_inbox', 'low_engagement', 'high_activity_time']]
        obs_sequence = np.array(observations).reshape(-1, 1)

        # Build and train the HMM
        model = hmm.MultinomialHMM(n_components=len(self.hidden_states), n_iter=100, random_state=42)
        # Define starting probability
        model.startprob_ = np.array([0.25, 0.25, 0.25, 0.25])
        # Define transition matrix
        model.transmat_ = np.array([
            [0.6, 0.2, 0.1, 0.1],
            [0.2, 0.5, 0.2, 0.1],
            [0.1, 0.2, 0.6, 0.1],
            [0.2, 0.2, 0.2, 0.4]
        ])
        # Define emission probability
        model.emissionprob_ = np.array([
            [0.1, 0.6, 0.2, 0.1],  # growth
            [0.2, 0.1, 0.5, 0.2],  # engagement
            [0.6, 0.1, 0.1, 0.2],  # support
            [0.3, 0.2, 0.1, 0.4]   # idle
        ])

        # Predict hidden states from observation sequence
        state_sequence = model.predict(obs_sequence)
        current_state = self.hidden_states[state_sequence[-1]]

        # Define simplified action policies
        state_action_map = {
            'growth': ['follow', 'like'],
            'engagement': ['comment', 'like'],
            'support': ['like'],         # restricted to 'like'
            'idle': ['like']             # restricted to 'like'
        }
        possible_actions = state_action_map[current_state]
        chosen_action = random.choice(possible_actions)

        # Output
        print("Current State:", current_state)
        print("Chosen Action:", chosen_action)
        return chosen_action