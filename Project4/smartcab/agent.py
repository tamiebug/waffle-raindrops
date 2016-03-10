import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from collections import namedtuple


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        print "LearningAgent.__init__ run"
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        
        # TODO: Initialize any additional variables here    
        self.actions = [None, 'forward', 'left', 'right']
        self.stateTuple = namedtuple('stateTuple', 
                        ['light','oncoming','right','left','next_waypoint'])
        self.stateActionTuple = namedtuple('stateActionTuple',
                        ['state', 'action'])                        
        self.Q = {}
        self.timesVisited = {}
        self.s_a = None
        self.reward = None
        self.netReward = 0
        self.debug = False
        
    def reset(self, destination=None):
        """ Resets the LearningAgent.  Also called after __init__ by the environment on start """
        self.planner.route_to(destination)
        self.s_a = None
        self.reward = None
        print "Self reward = {}".format(self.netReward)
        self.netReward = 0
        
    def update(self, t):
        # Q function learning parameters
        defaultVal = 3.
        epsilon = .07
        discountFactor = 1/2.
        isRandom = False
        
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        # TODO: Update state
        state = self.stateTuple( light                   = inputs['light'],
                                 oncoming                = inputs['oncoming'],
                                 right                   = inputs['right'],
                                 left                    = inputs['left'],
                                 next_waypoint           = self.next_waypoint,
                                 #deadline_approaching    = (deadline < 5),
                                )
        
        # Update Q function
        def findOptimalAction(state): 
            qVal = [defaultVal for i in range(4)]
            for i, action in enumerate(self.actions):
                s_a = self.stateActionTuple(state, action)
                if self.Q.has_key(s_a):
                    qVal[i] = self.Q[s_a]
                else:
                    self.Q[s_a] = defaultVal
            maxVal = max(qVal)
            #print "Q value of action is {}".format(maxVal)        
            return self.actions[ random.choice([i for i,j in enumerate(qVal) if j==maxVal]) ]
        
        optimal_s_a = self.stateActionTuple(state, findOptimalAction(state))
        if not self.s_a == None: # if this isn't the first time we run update(self, t)
            learningRate = 1./(5*self.timesVisited[self.s_a]+1)
            self.Q[self.s_a] = (1-learningRate) * self.Q[self.s_a] + \
                learningRate * (self.reward + discountFactor * (self.Q[optimal_s_a]))  
           
        # TODO: Select action according to your policy
        action = None
        optimalAction = findOptimalAction(state)
        
        # Choose whether to act optimally or act randomly
        if random.random() <= epsilon:
            action = self.actions[random.randint(0,3)]
            isRandom = True
        else:
            action = optimalAction
            
        # Execute action and get reward
        reward = self.env.act(self, action)
         
        # Update the old state variables
        self.s_a = self.stateActionTuple(state, action)
        
        if self.timesVisited.has_key(self.s_a):
            self.timesVisited[self.s_a] += 1
        else:
            self.timesVisited[self.s_a] =1
            
        self.reward = reward
        self.netReward += reward
        
        if self.debug:
            print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, random = {}, \waypoint =  {}".format(deadline, inputs, action, reward, isRandom, self.next_waypoint)

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e,update_delay=0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    
    a.debug = True
    sim = Simulator(e, update_delay=1)
    sim.run(n_trials=10)

if __name__ == '__main__':
    run()
