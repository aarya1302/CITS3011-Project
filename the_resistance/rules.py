import random
import numpy as np
from agent import Agent
class RuleBasedAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.is_spy_flag = False  # Track if this agent is a spy
        self.trust_levels = {}     # Track trust levels for other players
        self.missions_failed = 0    # Track the number of failed missions
        self.rounds_complete = 0     # Track the number of completed rounds

    def new_game(self, number_of_players, player_number, spies):
        self.is_spy_flag = player_number in spies  # Set if the agent is a spy
        self.trust_levels = {i: 0 for i in range(number_of_players)}  # Initialize trust levels for all players

    def propose_mission(self, team_size, betrayals_required):
        # Simple rule: Always propose a mission with trusted players
        team = []
        for player, trust in sorted(self.trust_levels.items(), key=lambda item: item[1], reverse=True):
            if len(team) < team_size:
                team.append(player)
            else:
                break
        return team

    def vote(self, mission, proposer, betrayals_required):
        # If a spy, reject missions with too many trusted players (to create doubt)
        if self.is_spy_flag and self.trust_levels[proposer] > 0:
            return False  # Spies may want to reject if they suspect a strong team
        return True  # Otherwise vote for the mission

    def betray(self, mission, proposer, betrayals_required):
        # If the agent is a spy, betray based on trust levels
        if self.is_spy_flag:
            return self.trust_levels[proposer] < 0  # Betray if the proposer is not trusted
        return False  # Resistance agents never betray

    def vote_outcome(self, mission, proposer, votes):
        # Update trust levels based on the outcome of the vote
        if len(votes) > 0:  # If the mission was approved
            for player in mission:
                self.trust_levels[player] += 1  # Trust increases for mission members
        else:
            for player in mission:
                self.trust_levels[player] -= 1  # Trust decreases for mission members

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        if not mission_success:
            self.missions_failed += 1  # Track failed missions
        # Update rounds complete after each mission
        self.rounds_complete += 1

    def round_outcome(self, rounds_complete, missions_failed):
        self.rounds_complete = rounds_complete
        self.missions_failed = missions_failed

    def game_outcome(self, spies_win, spies):
        if spies_win:
            print(f"Spies win! {self.name} was on the winning side.")
        else:
            print(f"Resistance wins! {self.name} was on the losing side.")
