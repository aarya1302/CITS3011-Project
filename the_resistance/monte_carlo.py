import random
from collections import defaultdict
from itertools import combinations
from agent import Agent
import numpy as np
class MonteCarloAgent(Agent):
    def __init__(self, name, epsilon=0.1):
        super().__init__(name)
        self.epsilon = epsilon  # Exploration rate
        self.q_table = defaultdict(float)  # Q-table for state-action values
        self.returns = defaultdict(list)  # To track all returns for each (state, action) pair
        self.episode = []  # Store the sequence of (state, action, reward) during an episode
        self.role = None  # "Spy" or "Resistance"
        self.player_number = None
        self.number_of_players = None
        self.spies = []

    def new_game(self, number_of_players, player_number, spies):
        '''
        Initializes the game, sets up game parameters, and determines if the agent is a spy or resistance.
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies
        self.role = "Spy" if spies else "Resistance"
        self.episode = []  # Clear the episode history for the new game

    def get_state(self, proposed_team, mission_history):
        '''
        Returns a representation of the current state. 
        This could include the proposed team, previous mission outcomes, etc.
        '''
        return tuple(proposed_team), tuple(mission_history)

    def choose_action(self, state, possible_actions):
        '''
        Chooses an action using an epsilon-greedy strategy.
        '''
        if random.uniform(0, 1) < self.epsilon:
            action = random.choice(possible_actions)  # Explore

            return action
        else:
            action = self.get_best_action(state, possible_actions)  # Exploit

            return action

    def get_best_action(self, state, possible_actions):
        '''
        Returns the best action based on the highest Q-value.
        '''
        q_values = [self.q_table.get((state, action), 0) for action in possible_actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(possible_actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def propose_mission(self, team_size, betrayals_required):
        '''
        Proposes a team for a mission. Uses Q-values to select the best team.
        '''
        possible_teams = list(combinations(range(self.number_of_players), team_size))
        state = self.get_state(possible_teams, [])
        best_team = self.choose_action(state, possible_teams)

        return list(best_team)

    def vote(self, mission, proposer, betrayals_required):
        '''
        Decides whether to vote for or against a mission proposal.
        '''
        state = self.get_state(mission, [])  # Adjust as needed
        possible_actions = [True, False]  # Vote for or against the mission
        action = self.choose_action(state, possible_actions)
        

        
        return action

    def vote_outcome(self, mission, proposer, votes):
        '''
        Receives the outcome of the vote. Records this step in the episode history.
        '''
        success = votes.count(True) > len(votes) // 2  # Majority votes needed for mission to proceed
        reward = 1 if success else -1
        state = self.get_state(mission, [])  # Define state as mission team and other contextual data
        action = tuple(mission)  # The action could be the proposed team or a vote-related action
        
        # Record this (state, action, reward) in the episode history
        self.episode.append((state, action, reward))

    def betray(self, mission, proposer, betrayals_required):
        '''
        Decides whether to betray the mission. Only spies can betray.
        '''
        if self.role == "Spy":
            state = self.get_state(mission, [])
            possible_actions = [True, False]  # Betray or not betray
            action = self.choose_action(state, possible_actions)

            return action
        
        return False

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        '''
        Receives the outcome of the mission and records it in the episode history.
        '''
        reward = 1 if mission_success else -1
        state = self.get_state(mission, [])
        action = tuple(mission)  # Or a specific action encoding, depending on your design
        
        # Record this (state, action, reward) in the episode history
        self.episode.append((state, action, reward))

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        Receives the outcome of each round.
        '''
        pass

    def game_outcome(self, spies_win, spies):
        '''
        Receives the outcome of the game and updates the Q-values based on the episode history.
        '''


        total_return = 1 if spies_win == (self.role == "Spy") else -1  # Reward depends on win/loss
        visited_state_actions = set()  # To avoid updating the same state-action pair multiple times

        # Update Q-values for each (state, action) pair in the episode
        for state, action, reward in self.episode:
            if (state, action) not in visited_state_actions:
                self.returns[(state, action)].append(total_return)
                self.q_table[(state, action)] = np.mean(self.returns[(state, action)])
                visited_state_actions.add((state, action))






