from agent import Agent
import random
import numpy as np

class EnhancedBayesianAgent(Agent):
    '''An enhanced implementation of a Bayesian agent for The Resistance'''
    


    def __init__(self, name='EnhancedBayesian', history=None):
        '''
        Initializes the agent with a belief table and historical data.
        '''
        self.name = name
        self.spies_history = history if history is not None else {}
        self.players_history = {}
    def calculate_prob_spy(self, player, evidence): 
        pass 

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        Initializes the game, setting up the belief system.
        '''
        self.number_of_players = number_of_players # current number of players
        self.player_number = player_number # agent's player number
        self.spy_list = spy_list # current list of spies 
        self.is_spy_flag = player_number in spy_list # if agent is a sply 
        
        self.spy_evidence = {}
        self.players_history = {i: {"failed_mission_member": 0, "failed_mission_votes": 0, "team_leader":0, "failed_team_leader":0}for i in range(number_of_players)}
        
        ''' Probability of being a spy is set to number of spies / number of players'''
        self.beliefs = np.full(number_of_players, round(((number_of_players - 1)/3))/(number_of_players-1))
        self.beliefs[player_number] = 0  # Agent knows it is not a spy

        # Initialize beliefs with prior knowledge
        self.initialize_beliefs()
        
        # ADD DEBUG LOG HERE 
        print(f"{self.players_history}")
        

    def initialize_beliefs(self):
        for player in range(self.number_of_players):
            if player in self.spies_history:
                spy_count = self.spies_history[player].count('spy')
                if spy_count > 0:
                    # Increase initial suspicion for known spies
                    self.beliefs[player] += spy_count * 0.1  # Arbitrary weight for prior knowledge

        # Normalize beliefs
        self.beliefs /= self.beliefs.sum()

    def is_spy(self):
        '''
        Returns True if the agent is a spy.
        '''
        return self.is_spy_flag

    def propose_mission(self, team_size, betrayals_required):
        '''
        Proposes a mission team by selecting players with the lowest probability of being a spy,
        but also considers players' historical success in missions.
        '''
        candidates = [(i, self.beliefs[i]) for i in range(self.number_of_players) if i != self.player_number]
        candidates.sort(key=lambda x: (x[1], self.get_success_rate(x[0])))  # Sort by belief and success rate
        team = [self.player_number]  # Always include self
        team.extend([x[0] for x in candidates[:team_size - 1]])
        return team

    def get_success_rate(self, player):
        '''Return a success rate for the player based on past missions.'''
        # Example implementation: needs historical data structure to store successes/failures
        if player in self.spies_history:
            successes = self.spies_history[player].count('success')
            total = len(self.spies_history[player])
            return successes / total if total > 0 else 0.5  # Default to 0.5 if no history
        return 0.5  # Default for players without history

    def vote(self, mission, proposer, betrayals_required):
        '''
        Votes for the mission considering not only trustworthiness but also historical mission outcomes.
        '''
        trustworthiness = sum([1 - self.beliefs[agent] for agent in mission])
        avg_trustworthiness = trustworthiness / len(mission)
        return avg_trustworthiness > 0.5 and self.consider_historical_votes(mission)

    def consider_historical_votes(self, mission):
        '''Evaluate historical voting patterns to decide on the mission.'''
        # Placeholder for more complex logic considering past votes
        # For now, we'll just use the trustworthiness
        return True  # Assume always trust the current voting context

    def vote_outcome(self, mission, proposer, votes):
        '''
        This method does nothing in the current implementation.
        '''
        pass  # No actions or updates performed

    def betray(self, mission, proposer, betrayals_required):
        '''
        Spies will betray strategically based on the number of betrayals required for failure.
        '''
        if self.is_spy():
            if betrayals_required == 1:
                return True  # Betray if a single betrayal is enough
            else:
                # Strategic betrayal based on mission context
                return random.random() < self.get_betrayal_probability(mission)
        return False

    def get_betrayal_probability(self, mission):
        '''Adjust betrayal probability based on mission composition and outcomes.'''
        if self.is_spy():
            return 0.7  # Example: more likely to betray if in a team of known 'resistance' players
        return 0.1  # Lower probability for non-spies

    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        '''
        Updates beliefs based on mission outcome.
        If the mission fails, increase suspicion on those in the mission.
        '''
        vote_failed_team = None
        selected_failed_team = None 
        
        # Updating Beliefs for players in mission
        self.update_history(mission, proposer, mission_success)
        
                


        # Normalize beliefs after updating
        self.beliefs /= self.beliefs.sum()

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        Updates belief at the end of each round.
        '''
        # No specific action required for now

    def game_outcome(self, spies_win, spies):
        '''
        Ends the game and resets the agent.
        '''
        # Nothing to update here, but could track statistics for self-improvement
        pass

    def update_history(self,mission,proposer, mission_success):
        """ Update the spy history for a player. """
        for agent in mission:
            if agent != self.player_number:
                if not mission_success:
                    self.players_history[proposer]["failed_team_leader"] += 1
                    self.players_history[agent]["failed_mission_member"]  += 1
                    self.beliefs[agent] *= 1.5  # Increase suspicion of those on failed missions
                else:
                    self.players_history[proposer]["team_leader"] += 1
                    
                    self.beliefs[agent] *= 0.8  # Decrease suspicion of those on successful missions

            
