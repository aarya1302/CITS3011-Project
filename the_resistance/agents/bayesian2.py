from agent import Agent
import random
import numpy as np


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
        
         # Object to keep track of player history
        self.current_mission_history = {"votes": [], "proposer": 0, "mission": [], "num_betrayals": 0}


        #keeps track of player history and probability that they're spies
        self.players_history = {player: {'failed_mission_votes': 0,
                                         'failed_mission_member': 0,
                                         'team_leader': 0,
                                         'failed_team_leader': 0,
                                         "probability": [2/3, 1/3]} #TODO change initial probability 
                                for player in range(number_of_players)}


######################## UTILS ################################
    def print_player_probabilities(self):
        for player, history in self.players_history.items():
            print(f"Player {player}: {history['probability']}")

    def update_state(self, mission, proposer, num_betrayals, mission_success):
        # Track failed mission members and proposers
        print(f"Updating state for Mission: {mission} Proposer: {proposer} Betrayals: {num_betrayals} Success: {mission_success} \n")
        # Add number of betrayals
        self.current_mission_history["num_betrayals"] = num_betrayals
        
        if not mission_success:
            self.players_history[proposer]['failed_team_leader'] += 1
             # Track votes for failed mission
            for player in self.current_mission_history["votes"]: 
                self.players_history[player]['failed_mission_votes'] += 1
                
            for player in mission:
                self.players_history[player]['failed_mission_member'] += 1
                
                print(f"Calculating Probability \n")
                self.calculate_spy_probability(player) 
            
                
        # Update proposer's leadership count
        self.players_history[proposer]['team_leader'] += 1
    
    def calculate_spy_probability(self, player):
        
      
        # Get the player's history
        history = self.players_history[player]

          # skip if we're sure that the player is a spy 
        
            
        if history["probability"][0] >= 1:
            return 1
        
        # Getting number of failed missions + 1 so that probability that player is a spy increases sequentially 
        
        num_failed_mission_mem = history['failed_mission_member'] if history['failed_mission_member'] > 0 else 1
        
        
        
        if(player in self.current_mission_history["mission"]):

            print(f"calculate_spy_probability for player: {player} current mission: {self.current_mission_history['mission']} num betrayals {self.current_mission_history['num_betrayals']}")

            #calculate probability of them being a spy based on number of betrayals 
            
            
            if self.current_mission_history["num_betrayals"] > 0:
                
                # probability of player being a spy based on number of betrayals num betrayals / number of players in mission
                
                p_team_member_is_spy = self.current_mission_history["num_betrayals"] / len(self.current_mission_history["mission"])
                
                #record player as spy if probability is 1.0
            
                if (p_team_member_is_spy == 1):
                    spy_prob = 1
                    self.players_history[player]["probability"] = [0,spy_prob]
                    return spy_prob
                
                print(f"p_team_member_is_spy num betrayals / people in mission : {p_team_member_is_spy}")
                
                '''
                Probability of Observation variable where P(S|Ot)= number of missions failed * ratio of spies to team members in mission (based on betrayal)
                '''
                o_p_failed_mission = [(1-p_team_member_is_spy)/num_failed_mission_mem, p_team_member_is_spy*num_failed_mission_mem]
                
                print(f"Previous belief {history['probability']} ")
                # updating belief on whether player is a spy 
                updated_belief = np.array(history['probability']) * np.array(o_p_failed_mission)
                
                #normalizing the probability 
                n = sum(updated_belief)
                updated_belief = updated_belief / n
                

                print(f"updated_belief {updated_belief}, num_failed_mission_mem {num_failed_mission_mem}, o_p_failed_mission {o_p_failed_mission}\n \n")
               
                
                self.players_history[player]["probability"] = updated_belief
                

          
            
            
            
        # Probability based on failed missions 
        p_num_failed_mission = (history['failed_mission_member'] / history['team_leader']) if history['team_leader'] > 0 else 0
        
    
            
        # # Probability based on failed missions as leader
        # p_failed_leader = (history['failed_team_leader'] / history['team_leader']) if history['team_leader'] > 0 else 0
        
        # # Probability based on voting for failed missions
        # p_voted_failed_mission = (history['failed_mission_votes'] / len(self.failed_missions)) if len(self.failed_missions) > 0 else 0
        
        
        # Store and print the calculated probability


        # returning probability of the player being a spy 
        return self.players_history[player]["probability"][1]


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
            print(f' Probability that player {player} is a  spy while voting : {self.players_history[player]["probability"][1]} \n ')
            if self.players_history[player]['probability'][1] > 0.5:  # Spy probability threshold can be adjusted
                # voting against 
                print(f"Voting against player {player}")
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

