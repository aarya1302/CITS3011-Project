import random
from collections import defaultdict
from itertools import combinations
from agent import Agent
import numpy as np

class QLearningAgent(Agent):
    def __init__(self, name, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(name)
        self.current_mission = None
        
        self.spy = False 
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = defaultdict(float)  # Q-table now stores player-specific values
        self.number_of_players = None
        self.player_number = None
        self.spies = []
    def new_game(self, number_of_players, player_number, spies):
        self.spy = False 
        self.q_table = defaultdict(float)  # Q-table now stores player-specific values
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies
        self.num_players = number_of_players
        self.player_number = player_number
    def print_q_values(self):
        '''
        Prints the Q-values in a nice format.
        '''
        print("\nQ-Values:")
        print("-------------------------------------------------")
        for key, value in self.q_table.items():
            
            player = key[0]
            action = key[1]
            print(f"Player: {player}, Action: {action}, Q-Value: {value}")
        print("-------------------------------------------------")


    def get_state(self, team_or_player):
        '''
        The state will be the sorted team if a team is provided,
        or just the player as a tuple if a single player is provided.
        '''
        if isinstance(team_or_player, (list, tuple)):  # If it's a team (list/tuple)
            return tuple(sorted(team_or_player))  # Sort to avoid ordering issues
        else:  # If it's a single player
            return (team_or_player,)  # Return as a tuple to keep the state consistent

    def choose_action(self, team):
        '''
        Chooses an action (vote for or against the team) based on Q-values.
        '''
        
        if random.uniform(0, 1) < self.epsilon:
            return random.choice([True, False])  # Randomly vote for or against (exploration)
        else:
            return self.get_best_action(team)  # Choose based on learned Q-values (exploitation)

    def propose_team(self, team_size):
            '''
            Propose a team based on Q-values for other players.
            If exploration is chosen, randomly select a team.
            If exploitation is chosen, select players with the highest Q-values.
            '''
            if random.uniform(0, 1) < self.epsilon:
                # Exploration: randomly propose a team
                return random.sample(range(self.number_of_players), team_size)
            else:
                # Exploitation: propose the best team based on learned Q-values
                players = [i for i in range(self.number_of_players) if i != self.player_number]
                q_values = {player: max(self.q_table[(self.get_state([player]), True)], 
                                        self.q_table[(self.get_state([player]), False)]) for player in players}
                
                # Sort players by their Q-values and select the best ones for the team
                sorted_players = sorted(q_values, key=q_values.get, reverse=True)
                return sorted_players[:team_size]


    def get_best_action(self, state):
        '''
        Get the best action (True/False) based on Q-values for the current state.
        '''
        

        for player in state:
            #print(f"Q values: {player} {q_yes} {q_no}")
            
            if self.q_table[(player, True)] <0:
                #print("Voting false")
                return False
        return True
            

    def update_q_value(self, team, action, reward):
        '''
        Updates the Q-value for each player in the team based on mission success or failure.
        '''
        team = tuple(team)

        # Loop through each player in the team
        for player in team:
            player_state_action = (player, action)

            # Initialize player Q-value if not present
            if player_state_action not in self.q_table:
                self.q_table[player_state_action] = 0
                
            # Get current Q-value for the player
            player_current_q = self.q_table[player_state_action]
            
            # Calculate the max future Q-value for the player
            player_future_q = max(self.q_table.get((player, True), 0), self.q_table.get((player, False), 0))

            # Update the Q-value for the current action taken by the player
            self.q_table[player_state_action] = player_current_q + self.alpha * (reward + self.gamma * player_future_q - player_current_q)


    def vote(self, mission, proposer, betrayals_required):
        '''
        Decide whether to vote for or against the mission based on the Q-values for the team.
        '''
        action = self.choose_action(mission)
        #print(action)
        return action

    def vote_outcome(self, mission, proposer, votes):
        '''
        Receives the outcome of the vote and updates Q-values based on the result.
        If the mission fails, decrease Q-value for voting for any team containing players from the failed team.
        If the mission succeeds, increase Q-value for those players.
        '''
    

        # If mission was approved, it will proceed. Otherwise, no reward/punishment for this mission.
    def betray(self, mission, proposer, betrayals_required):
        """
        Spy betrayal logic: weigh how risky betrayal is.
        Only betray when necessary or strategically advantageous.
        """
        if self.player_number in self.spies:

            num_spies_on_mission = sum(1 for member in mission if member in self.spies)
            if num_spies_on_mission >= betrayals_required:
                return True
            # Betray randomly with a 30% chance, depending on game state
            return random.random() < 0.3
        return False

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        '''
        After a mission succeeds or fails, update Q-values for each player on the mission.
        '''
        self.current_mission = {'mission': mission, 'proposer': proposer, 'num_betrayals': num_betrayals, 'mission_success': mission_success}
        reward = 1 if mission_success else -1
        self.update_q_value(mission, True, reward)
        self.print_q_values()
        # For each player in the mission, adjust their Q-value for being part of that mission
        