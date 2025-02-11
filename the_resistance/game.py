from agent import Agent
import random

class Game:
    '''
    A class for maintaining the state of a game of The Resistance.
    A agent oriented architecture is maintained where the 
    game has a list of Agents and methods are called on those agents 
    to share information and get game actions
    '''

    def __init__(self, agents):
        '''
        agents is the list of agents playing the game
        the list must contain 5-10 agents
        This method initiaises the game by
        - shuffling the agents
        - randomly assigning spies
        - calling the new_game method on all agents
        - build a scoreboard and data structures
        '''
        if len(agents)<5 or len(agents)>10:
            raise Exception('Agent array out of range')
        #clone and shuffle agent array
        self.agents = agents.copy()
        random.shuffle(self.agents)
        self.num_players = len(agents)
        #allocate spies
        self.spies = []
        while len(self.spies) < Agent.spy_count[self.num_players]:
            spy = random.randrange(self.num_players)
            if spy not in self.spies:
                self.spies.append(spy)
        #start game for each agent        
        for agent_id in range(self.num_players):
            spy_list = self.spies.copy() if agent_id in self.spies else []
            self.agents[agent_id].new_game(self.num_players,agent_id, spy_list)
        #initialise rounds
        self.missions_failed = 0
        self.rounds = []
            

    def play(self):
        leader_id = 0
        for i in range(5): 
            self.rounds.append(Round(leader_id,self.agents, self.spies, i))
            if not self.rounds[i].play(): self.missions_failed+= 1
            for a in self.agents:
                a.round_outcome(i+1, self.missions_failed)
            leader_id = (leader_id+len(self.rounds[i].missions)) % len(self.agents)    
        for a in self.agents:
            a.game_outcome(self.missions_failed>2, self.spies)

    def __str__(self):
        s = 'Game between agents: [{}]'.format(", ".join([str(agent) for agent in self.agents])) 
        for r in self.rounds:
            s = s + '\n' + str(r)
        if self.missions_failed<3:
            s = s + '\nThe Resistance succeeded!'
        else:
            s = s + '\nThe Resistance failed!'
        s = s + '\nThe spies were agents: [{}]'.format(", ".join([str(self.agents[i]) for i in self.spies])) 
        return s

    def get_results(self):
        resistance_agents = []
        spy_agents = []
        for agent_id in range(self.num_players):
            agent = self.agents[agent_id]
            if agent_id in self.spies:
                spy_agents.append(agent)
            else:
                resistance_agents.append(agent)

        if self.missions_failed < 3:
            # Resistance victory
            #            winning team       losing team
            return True, resistance_agents, spy_agents
        else:
            # Spy victory
            return False, spy_agents,  resistance_agents

class Round():
    '''
    a representation of a round in the game.
    '''

    def __init__(self, leader_id, agents, spies, rnd):
        '''
        leader_id is the current leader (next to propose a mission)
        agents is the list of agents in the game,
        spies is the list of indexes of spies in the game
        rnd is what round the game is up to 
        '''
        self.leader_id = leader_id
        self.agents = agents
        self.spies = spies
        self.rnd = rnd
        self.missions = []

    def __str__(self):
        '''
        produces a string representation of the round
        '''
        s = 'Round:' + str(self.rnd + 1)
        for m in self.missions:
            s = s +'\n'+str(m)
        if self.is_successful():
            s = s + '\nResistance won the round.'
        else:
            s = s + '\nResistance lost the round.'
        return s    

    def __repr__(self):
        '''
        produces a formal representation of the round
        '''
        s = 'Round(leader_id=' + self.leader_id \
                + ', agents=' + self.agents \
                + ', rnd=' + self.rnd \
                + ', missions=' + self.missions+')'
        return s        

    def play(self):
        '''
        runs team assignment until a team is approved
        or five missions are proposed, 
        and returns True is the final mission was successful
        '''
        mission_size = Agent.mission_sizes[len(self.agents)][self.rnd]
        betrayals_required = Agent.betrayals_required[len(self.agents)][self.rnd]
        while len(self.missions)<5:
            team = self.agents[self.leader_id].propose_mission(mission_size, betrayals_required)
            mission = Mission(self.leader_id, team, self.agents, self.spies, self.rnd, len(self.missions)==4)
            self.missions.append(mission)
            self.leader_id = (self.leader_id+1) % len(self.agents)
            if mission.is_approved():
                return mission.is_successful()
        return mission.is_successful()   

    def is_successful(self):
        '''
        returns true is the mission was successful
        '''
        return len(self.missions)>0 and self.missions[-1].is_successful()


class Mission():
    '''
    a representation of a proposed mission
    '''
    
    def __init__(self, leader_id, team, agents, spies, rnd, auto_approve):
        '''
        leader_id is the id of the agent who proposed the mission
        team is the list of agent indexes on the mission
        agents is the list of agents in the game,
        spies is the list of indexes of spies in the game
        rnd is the round number of the game
        auto_approve is true if this is the fifth mission proposed this round, and no vite is required.
        '''
        self.leader_id = leader_id
        self.team = team
        self.agents = agents
        self.spies = spies
        self.rnd = rnd
        self.run(auto_approve)

    def run(self, auto_approve):    
        '''
        Runs the mission, by asking agents to vote, 
        and if the vote is in favour,
        asking spies if they wish to fail the mission
        '''
        betrayals_required = Agent.betrayals_required[len(self.agents)][self.rnd]
        self.votes_for = [i for i in range(len(self.agents)) if auto_approve or self.agents[i].vote(self.team, self.leader_id, betrayals_required)]
        for a in self.agents:
            a.vote_outcome(self.team, self.leader_id, self.votes_for)
        if 2*len(self.votes_for) > len(self.agents):
            self.betrayals = [i for i in self.team if i in self.spies and self.agents[i].betray(self.team, self.leader_id, betrayals_required)]
            success = len(self.betrayals) < betrayals_required
            for a in self.agents:
                a.mission_outcome(self.team,self.leader_id, len(self.betrayals), success)

    def __str__(self):
        '''
        Gives a string representation of the mission
        '''
        s = 'Leader:'+str(self.agents[self.leader_id])+'\nTeam: '
        for i in self.team:
            s += str(self.agents[i])+', '
        s = s[:-2]+'\nVotes for: '
        for i in self.votes_for:
            s+= str(self.agents[i])+', '
        if self.is_approved():    
            s = s[:-2]+'\nBetrayals recorded:'+ str(len(self.betrayals))
            s += '\nMission '+ ('Succeeded' if self.is_successful() else 'Failed')
        else:
            s = s[:-2]+'\nMission Aborted'
        return s

    def __repr__(self):
        '''
        Creates formal (json) representation of the mission
        '''
        return 'Mission(leader_id='+ self.agents[self.leader_id] \
                       + ', team='+self.team \
                       +', agents='+self.agents \
                       +', rnd='+self.rnd \
                       +', votes_for='+self.votes_for \
                       +', betrayal_num=' +len(self.betrayals)+')'

    
    def is_approved(self):
        '''
        Returns True if the mission is approved, 
        False if the mission is not approved,
        and 
        Raises an exception if the mission has not yet had the votes recorded
        '''
        return 2*len(self.votes_for) > len(self.agents)

    def is_successful(self):
        '''
        Returns True is no agents failed the mission 
        (or only one agent failed round 4 in a game of 7 or more players)
        raises an exception if the mission is not approved or betrayals not recorded.
        '''
        return self.is_approved() and len(self.betrayals) < Agent.betrayals_required[len(self.agents)][self.rnd]
