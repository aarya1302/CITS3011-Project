import random
import numpy as np
from agent import Agent

class BayesianHMM_Agent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.num_players = 0
        self.spy_probabilities = []  # Probability of each player being a spy
        self.trust_matrix = []  # Trust-Suspicion matrix
        self.spy = False  # Whether this agent is a spy
        self.spies = []  # List of spies if this agent is one
        self.mission_histories = []  # History of mission outcomes (success/fail)
        self.vote_histories = []  # History of votes
        self.round_number = 0  # Tracks the current 
    
    def new_game(self, number_of_players, player_number, spies):
        """
        Initializes the game state.
        """
        self.num_players = number_of_players
        self.player_number = player_number
        self.spies = spies
        self.spy = player_number in spies
        self.spy_probabilities = [1 / (number_of_players - 1)] * number_of_players
        self.spy_probabilities[self.player_number] = 0  # Set self to 0% spy probability
        self.trust_matrix = [0] * number_of_players  # Start with neutral trust for everyone
        self.mission_histories = []
        self.vote_histories = []
        self.round_number = 0
        

    
    def propose_mission(self, team_size, betrayals_required):
        """
        Propose a team with the lowest spy probabilities. Spies choose strategically based on trust and suspicion.
        """
        if self.spy:
            # Spy strategy: balance between selecting spies and non-suspects
            team = self.select_spy_team(team_size)
        else:
            # Select the team with the lowest suspected spy probabilities
            team = np.argsort(self.spy_probabilities)[:team_size].tolist()

        self.mission_histories.append({"team": team, "proposer": self.player_number})
        return team

    def select_spy_team(self, team_size):
        """
        Spy strategy for proposing a mission, mixing spies and non-suspects.
        """
        non_spies = [i for i in range(self.num_players) if i not in self.spies]
        # Include self as a spy and a mix of non-spies for lower suspicion
        team = random.sample(non_spies, team_size - 1) + [self.player_number]
        return team

    def vote(self, mission, proposer, betrayals_required):
        """
        Vote based on spy probabilities and trust matrix.
        Resistance players vote against suspicious teams.
        Spies vote strategically.
        """
        spy_prob = sum(self.spy_probabilities[member] for member in mission)
        trust_level = sum(self.trust_matrix[member] for member in mission)

        if self.spy:
            # Spy logic: vote yes if there's a good chance spies are in, no otherwise
            if any(member in self.spies for member in mission):
                return True  # Approve if a spy is on the mission
            return False  # Reject if the team looks too good for Resistance
        else:
            # Resistance logic: vote based on low spy suspicion and higher trust
            return spy_prob < 0.4 and trust_level > 0

    def betray(self, mission, proposer, betrayals_required):
        """
        Spy betrayal logic: weigh how risky betrayal is.
        Only betray when necessary or strategically advantageous.
        """
        if self.spy:
            num_spies_on_mission = sum(1 for member in mission if member in self.spies)
            if num_spies_on_mission >= betrayals_required:
                return True
            # Betray randomly with a 30% chance, depending on game state
            return random.random() < 0.3
        return False

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        """
        Update beliefs based on mission outcome and update trust matrix.
        Also adjust trust for the proposer based on mission success or failure.
        """
        self.mission_histories.append({
            'mission': mission, 
            'proposer': proposer,
            'num_betrayals': num_betrayals,
            'mission_success': mission_success
        })


        if mission_success:
            self.update_beliefs(mission, success=True)
            self.trust_matrix[proposer] += 1  # Increase trust for proposer if the mission succeeds
        else:
            self.update_beliefs(mission, success=False)
            self.trust_matrix[proposer] -= 1  # Decrease trust for proposer if the mission fails

    def update_beliefs(self, mission, success):
        """
        Bayesian updating of spy probabilities based on mission outcomes.
        Dynamic weighting of updates based on mission size and context.
        """
        for player in mission:
            if not success:
                # Increase suspicion if mission failed
                self.spy_probabilities[player] = min(self.spy_probabilities[player] * 1.3, 1.0)
                self.trust_matrix[player] -= 1  # Lower trust for failure
            else:
                # Decrease suspicion if mission succeeded
                self.spy_probabilities[player] = max(self.spy_probabilities[player] * 0.7, 0.0)
                self.trust_matrix[player] += 1  # Increase trust for success

    def vote_outcome(self, mission, proposer, votes):
        """
        Track voting patterns to further refine the trust matrix.
        Players who vote against successful teams may increase suspicion.
        """
        self.vote_histories.append({
            'mission': mission, 
            'proposer': proposer,
            'votes': votes
        })

        for i, vote in enumerate(votes):
            if vote == False and self.trust_matrix[i] > 0:
                # Reduce trust if someone votes against a trusted mission
                self.trust_matrix[i] -= 0.5

    def round_outcome(self, rounds_complete, missions_failed):
        """
        Updates the round number and track the overall progress of the game.
        """
        self.round_number = rounds_complete

    def game_outcome(self, spies_win, spies):
        """
        Informs the agent of the final outcome of the game.
        """
        pass
