from agent import Agent
import random

class EnhancedHeuristicAgent(Agent):
    '''An enhanced heuristic-based agent for The Resistance game.'''

    def __init__(self, name='EnhancedHeuristicAgent'):
        self.name = name
        self.failed_missions = []
        self.successful_missions = []
        self.vote_history = {}
        self.vote_counts = {}

    def new_game(self, number_of_players, player_number, spy_list):
        '''Reset the agent's knowledge for a new game.'''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list
        self.failed_missions = []
        self.successful_missions = []
        self.vote_history = {i: [] for i in range(number_of_players) if i != player_number}
        self.vote_counts = {i: 0 for i in range(number_of_players) if i != player_number}

    def is_spy(self):
        '''Check if this agent is a spy.'''
        return self.player_number in self.spy_list

    def propose_mission(self, team_size, betrayals_required):
        '''Propose a mission team based on heuristics.'''
        candidates = [i for i in range(self.number_of_players) if i != self.player_number]
        
        # Filter out players who have consistently failed missions
        candidates = [p for p in candidates if p not in self.failed_missions]
        
        # If not enough candidates remain, include all players
        if len(candidates) < team_size - 1:
            candidates = [i for i in range(self.number_of_players) if i != self.player_number]

        # Select the first team_size - 1 candidates randomly
        selected_team = random.sample(candidates, min(team_size - 1, len(candidates)))
        selected_team.append(self.player_number)  # Always include self
        return selected_team

    def vote(self, mission, proposer, betrayals_required):
        '''Vote for the mission based on historical player behavior.'''
        # Count the votes against successful missions from team members
        fail_count = sum(1 for player in mission if player in self.failed_missions)
        trust_threshold = 0.5  # Adjustable trust threshold

        # Heuristic: Accept the mission if the trustworthiness of the team is above the threshold
        if fail_count > 0 or (fail_count / len(mission)) > trust_threshold:
            return False  # Reject the mission
        return True  # Accept the mission

    def vote_outcome(self, mission, proposer, votes):
        '''This method does nothing in the current implementation.'''
        pass  # No actions or updates performed

    def betray(self, mission, proposer, betrayals_required):
        '''Determine whether to betray based on player actions and trust levels.'''
        if self.is_spy() and len(mission) > 1:  # Only betray if there's a chance to sway the outcome
            # Heuristic: If a mission contains players who have voted against successful missions, consider betraying
            if any(player in self.vote_counts and self.vote_counts[player] > 0 for player in mission):
                return True  # Betray
        return False  # Don't betray

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        '''Update history based on the outcome of the mission.'''
        if not mission_success:
            self.failed_missions.extend(mission)  # Track failed mission players
        else:
            self.successful_missions.append(mission)  # Track successful mission

        # Update vote history for players involved in the mission
        for player in mission:
            # Only update vote history for players that exist in the vote_history
            if player in self.vote_history:
                self.vote_history[player].append(not mission_success)  # Append the outcome
            else:
                self.vote_history[player] = [not mission_success]  # Initialize if not present


    def round_outcome(self, rounds_complete, missions_failed):
        '''Analyze the round outcomes for player behavior.'''
        for player in self.vote_history:
            self.vote_counts[player] = sum(1 for vote in self.vote_history[player] if not vote)  # Count votes against

    def game_outcome(self, spies_win, spies):
        '''Reset agent states at the end of the game.'''
        self.failed_missions.clear()
        self.successful_missions.clear()
        self.vote_history.clear()
        self.vote_counts.clear()
