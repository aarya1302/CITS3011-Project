from agent import Agent
import random
import numpy as np
import math


class BayesianAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.players_history = {}
        self.spy_count = {5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4}
        self.spies = []
    
    def is_spy(self):
        return self.player_number in self.spies

    def new_game(self, number_of_players, player_number, spies):
        self.number_of_players = number_of_players
        self.player_number = player_number
        
        # Keeps track of predicted spies
        self.spies = spies if spies else []
        
         # Object to keep track of mission history

        self.current_mission_history = {"votes": [], "proposer": 0, "mission": [], "num_betrayals": 0, "mission_success": True}
        self.num_failed_missions = 0

        #keeps track of player history and probability that they're spies
        self.players_history = {player: {'failed_mission_votes': 0,
                                         'failed_mission_member': 0,
                                         'team_leader': 0,
                                         'failed_team_leader': 0,
                                         "probability": [2/3, 1/3]} 
                                for player in range(number_of_players) if player != self.player_number}

######################## UTILS ################################
    def print_player_probabilities(self):
        for player, history in self.players_history.items():
            print(f"Player {player}: {history['probability']}")
    def get_current_spies(self): 
        # Sort all players by their spy probability in descending order
        players_sorted_by_spy_probability = sorted(self.players_history.keys(), 
                                                key=lambda x: self.players_history[x]['probability'][1], 
                                                reverse=True)
        
        # Get the top 2 players with the highest spy probability
        num_spies = math.ceil(self.number_of_players / 3)
        
        
        top_spy_candidates = players_sorted_by_spy_probability[:num_spies]  # Top 2 players with highest probability

        
        print(f"Top 2 players suspected as spies based on probabilities: {top_spy_candidates}")
        
        return top_spy_candidates
        

    def update_state(self, mission, proposer, num_betrayals, mission_success):
        # Track failed mission members and proposers
        print(f"Updating state for Mission: {mission} Proposer: {proposer} Betrayals: {num_betrayals} Success: {mission_success} \n")
        # Add number of betrayals
        self.current_mission_history["num_betrayals"] = num_betrayals
        
        
        if not mission_success:
            if proposer != self.player_number:
                self.players_history[proposer]['failed_team_leader'] += 1
            
             # Track votes for failed mission
            for player in self.current_mission_history["votes"]: 
                if player != self.player_number:
                    self.players_history[player]['failed_mission_votes'] += 1
                
            for player in mission:
                if player != self.player_number:
                    self.players_history[player]['failed_mission_member'] += 1
                        
                    print(f"Calculating Probability \n")
                    self.players_history[player]['probability'] = self.calculate_spy_probability(player) 
                
            self.normalize_probabilities()
                
        # Update proposer's leadership count
        if proposer != self.player_number:
            self.players_history[proposer]['team_leader'] += 1
    
    def normalize_probabilities(self):
        """
        Normalize the spy probabilities across all players
        so that the sum of spy probabilities equals 1.
        """
        print(self.players_history)
        spy_probs = [self.players_history[player]["probability"][1] for player in self.players_history]
        total_prob = sum(spy_probs)
     

        if total_prob > 0:
            for player in self.players_history:

                self.players_history[player]["probability"][1] /= total_prob
                self.players_history[player]["probability"][0] = 1 - self.players_history[player]["probability"][1]
        else:
            # If the total probability is 0, keep the probabilities unchanged
            print("Warning: Total probability of spies is 0. No normalization applied.")
            
        self.print_player_probabilities()

    def calculate_prob_failed_mission(self, player, history):
         # Getting number of failed missions so that probability that player is a spy increases sequentially 
        
        num_failed_mission_mem = history['failed_mission_member'] + 1  if history['failed_mission_member'] > 0 else 1
        
        
        if(player in self.current_mission_history["mission"] and player != self.player_number):

            print(f"calculate_spy_probability for player: {player} current mission: {self.current_mission_history['mission']} num betrayals {self.current_mission_history['num_betrayals']}")
            
            # Calculate probability of them being a spy based on number of betrayals 
            
            if self.current_mission_history["num_betrayals"] > 0:
            
                '''
                Probability of player being a spy based on 
                
                        num betrayals / number of players in mission
                '''
                p_team_member_is_spy = self.current_mission_history["num_betrayals"] / len(self.current_mission_history["mission"])
                
               
                #record player as spy if probability is 1.0
            
                if (p_team_member_is_spy == 1):
                    spy_prob = 1 
                    return [0,spy_prob]
                
                
                print(f"p_team_member_is_spy num betrayals / people in mission : {p_team_member_is_spy}")
                
                '''
                Probability of Observation variable where P(Ot|St)
                
                    Resistance  1 - ratio of spies to team members in mission (based on betrayal) / number of failed missions
                    
                    Spy    ratio of spies to team members in mission (based on betrayal) * number of failed missions
                
                o_p_failed_mission = [P if player is resistance, P if player is spy]
                    
                '''
                o_p_failed_mission = [(1-p_team_member_is_spy)/num_failed_mission_mem, p_team_member_is_spy*num_failed_mission_mem]
                
                #o_p_failed_leader = [1-(history['failed_team_leader'] / history['team_leader']), (history['failed_team_leader'] / history['team_leader'])]
                print(f"Previous belief {history['probability']} ")
                
                
                # updating belief on whether player is a spy 
                updated_belief = np.array(history['probability']) * np.array(o_p_failed_mission)
                
                #normalizing the probability 
                n = sum(updated_belief)
                updated_belief = updated_belief / n
                
                

                print(f"updated_belief {updated_belief}, num_failed_mission_mem {num_failed_mission_mem}, o_p_failed_mission {o_p_failed_mission}\n \n")
               
                
                return updated_belief
                
    def calculate_prob_failed_vote(self, player, history, updated_belief):
        
        if(player in self.current_mission_history["votes"] and not self.current_mission_history["mission_success"] and player != self.player_number):
            
            ratio_voted_failed_mission = (history["failed_mission_votes"] / self.num_failed_missions) 
            print(f"failed mission votes: {history['failed_mission_votes']} num failed missions {self.num_failed_missions} ratio {ratio_voted_failed_mission}")
            print(f"calculate_spy_probability for player: {player} current votes: {self.current_mission_history['votes']} ")
            
            
            p_voted_failed_mission = np.array([(1-ratio_voted_failed_mission) if ratio_voted_failed_mission < 1 else 1, ratio_voted_failed_mission])
            o_p_voted_failed_mission = np.array([0.4, 0.7]) * p_voted_failed_mission

            print(f"Previous belief {updated_belief} ")
                
            
            # updating belief on whether player is a spy 
            history['probability'] =  updated_belief* np.array(o_p_voted_failed_mission)
                
             #normalizing the probability 
            n = sum(updated_belief)
            updated_belief = updated_belief / n   
                
            #normalize belief across players 
                

            print(f"updated_belief {updated_belief},  o_p_voted_failed_mission {o_p_voted_failed_mission}\n \n")

            return updated_belief
        else: 
            return updated_belief
    
    def calculate_spy_probability(self, player):
        
      
        # Get the player's history
        history = self.players_history[player]
        
        # skip if we're sure that the player is a spy 
           
        if history["probability"][0] >= 1:
            return 1
        
        # Calculating probability of player being a spy based on number of betrayals and failed mission 
        updated_belief  = self.calculate_prob_failed_mission(player, history)
       
            
        # Probability based on failed missions 
        #p_num_failed_mission = (history['failed_mission_member'] / history['team_leader']) if history['team_leader'] > 0 else 0
        
    
            
        # # Probability based on failed missions as leader
        
        
        
        # # Probability based on voting for failed missions
        updated_belief = self.calculate_prob_failed_vote(player, history, updated_belief)
        
        
        
        
        
        # Store and print the calculated probability


        # returning probability of the player being a spy 
        return updated_belief


############################ ACTIONS #######################
    def propose_mission(self, team_size, betrayals_required):
        # Sort players by lowest spy probability and pick the least likely spies
        players_sorted_by_spy_probability = sorted(self.players_history.keys(), key=lambda x: self.players_history[x]['probability'][1])
        
        #TODO account for when player is a spy 
            
        print(f"Player{self.player_number}Proposed team: {players_sorted_by_spy_probability[:team_size]} \n")
        return players_sorted_by_spy_probability[:team_size]

    def vote(self, mission, proposer, betrayals_required):
        # Vote against a mission if it includes players with high spy probability
        
        print(f"Current Player: {self.player_number}")
        for player in mission:
            if player != self.player_number:
                print(f' Probability that player {player} is a  spy while voting : {self.players_history[player]["probability"][1]} ')
                curr_spies =  self.get_current_spies()
                # Check if the current player is one of the top 2 suspected spies
                print("Is player a top spy ", player in curr_spies)
                if player in curr_spies and self.num_failed_missions > 0:
                    print(f"Player {player} is among the top spies suspects, voting False. \n")
                    return False

        return True

    def betray(self, mission, proposer, betrayals_required):
        # As a spy, betray only when necessary or when sabotage can succeed
        if self.player_number in self.spies:
            num_spies_on_mission = len([player for player in mission if player in self.spies])
            # Betray if the number of spies on the mission ensures success
            if num_spies_on_mission >= betrayals_required:
                return True
        return False



######################### OUTCOMES #############################
    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        
        self.current_mission_history["votes"] = votes 
        self.current_mission_history["proposer"] = proposer
        self.current_mission_history["mission"] = mission
        
        print(f"Votes {votes} Proposed Mission {mission} Proposer {proposer} \n")
        pass
    def mission_outcome(self, mission, proposer, num_betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        num_betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.
        '''
        self.current_mission_history["mission_success"] = mission_success
        if not mission_success: 
            self.num_failed_missions += 1
            
        self.update_state(mission, proposer, num_betrayals, mission_success)

        


        pass

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''

        
        pass
    
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        
        pass

