from agent import Agent
import numpy as np
import random

class ReinforcementLearningAgent(Agent):
    '''A reinforcement learning agent for The Resistance game using Q-learning.'''

    def __init__(self, name='ReinforcementLearningAgent'):
        self.name = name
        self.q_table = {}
        self.exploration_rate = 1.0
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.min_exploration_rate = 0.01
        self.exploration_decay = 0.995

    def new_game(self, number_of_players, player_number, spy_list):
        '''Reset the agent's knowledge for a new game.'''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list
        self.q_table = {}  # Reset Q-table for new game
        self.exploration_rate = 1.0  # Reset exploration rate

    def get_state(self):
        '''Represent the current state as a tuple.'''
        # A state can include player roles and history; customize as needed
        state = (self.player_number, tuple(self.spy_list))
        return state

    def propose_mission(self, team_size, betrayals_required):
        '''Propose a mission team based on Q-learning.'''
        state = self.get_state()
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.number_of_players)  # Initialize Q-values

        # Choose action based on exploration/exploitation
        if random.uniform(0, 1) < self.exploration_rate:
            # Explore: randomly select players
            candidates = [i for i in range(self.number_of_players) if i != self.player_number]
            selected_team = random.sample(candidates, min(team_size - 1, len(candidates)))
            selected_team.append(self.player_number)  # Always include self
            return selected_team
        else:
            # Exploit: choose the best action (team proposal based on Q-values)
            best_action = np.argmax(self.q_table[state])
            selected_team = [best_action]  # Team proposal logic will need to be customized
            selected_team.append(self.player_number)
            return selected_team

    def vote(self, mission, proposer, betrayals_required):
        '''Vote for the mission based on Q-learning.'''
        state = self.get_state()
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.number_of_players)

        # For simplicity, vote randomly for now; implement learning-based voting logic later
        return random.choice([True, False])

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        '''Update Q-table based on the mission outcome.'''
        state = self.get_state()
        action = self.propose_mission(len(mission), 0)  # Get action for the mission
        
        # Reward structure
        reward = 1 if mission_success else -1
        
        # Update Q-values
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.number_of_players)

        best_next_state = self.get_state()  # Assuming the next state is the same for simplicity
        if best_next_state not in self.q_table:
            self.q_table[best_next_state] = np.zeros(self.number_of_players)

        td_target = reward + self.discount_factor * np.max(self.q_table[best_next_state])
        td_delta = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_delta

    def round_outcome(self, rounds_complete, missions_failed):
        '''Decay exploration rate over time.'''
        if self.exploration_rate > self.min_exploration_rate:
            self.exploration_rate *= self.exploration_decay

    def game_outcome(self, spies_win, spies):
        '''Reset agent states at the end of the game.'''
        self.q_table.clear()  # Clear Q-table
