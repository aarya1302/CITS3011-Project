import pkgutil, importlib, inspect, random, math
import matplotlib.pyplot as plt

from game import Game
from agent import Agent
from agent_handler import AgentHandler

# Configuration
NUMBER_OF_TOURNAMENTS = 10
NUMBER_OF_GAMES_PER_TOURNAMENT = 100
PRINT_GAME_EVENTS = False
LEADERBOARD_LINES = 10
LEADERBOARD_WIDTH = 200
IGNORE_AGENTS = []

# Metrics for specific agents
TARGET_AGENTS = ["HMM", "SatisfactoryAgent", "BasicAgent", "RandomAgent"]

# Agent discovery and setup
agent_name_length = 0
agent_fullname_length = 0
agent_classes = []
agent_pool = []

agent_class_names = set()
agent_class_fullnames = {}
duplicates_exist = False

# Find agents in the agents folder
for item in pkgutil.iter_modules(["agents"]):
    package_name = "agents.{}".format(item.name)
    package = importlib.import_module(package_name)
    for name, cls in inspect.getmembers(package, inspect.isclass):
        if issubclass(cls, Agent) and cls is not Agent:
            if name in IGNORE_AGENTS:
                continue

            if name in agent_class_names:
                duplicates_exist = True
            agent_class_names.add(name)

            agent_classes.append(cls)

            if len(name) > agent_name_length:
                agent_name_length = len(name)

            fullname = cls.__module__ + "." + cls.__name__
            agent_class_fullnames[cls] = fullname
            if len(fullname) > agent_fullname_length:
                agent_fullname_length = len(fullname)

def create_agent(agent_cls):
    agent_name = "{}{}".format(agent_cls.__name__[:3].lower(), len(agent_pool))
    agent = agent_cls(name=agent_name)
    agent = AgentHandler(agent)
    agent.orig_class = agent_cls
    return agent

def print_leaderboard(scores):
    leaderboard = []

    for agent_cls in agent_classes:
        agent_scores = scores[agent_cls]
        win_rate = agent_scores["wins"] / agent_scores["games"] if agent_scores["games"] else 0
        res_win_rate = agent_scores["res_wins"] / agent_scores["res"] if agent_scores["res"] else 0
        spy_win_rate = agent_scores["spy_wins"] / agent_scores["spy"] if agent_scores["spy"] else 0

        if duplicates_exist:
            agent_name = ("{:" + str(agent_fullname_length) + "}").format(agent_class_fullnames[agent_cls])
        else:
            agent_name = ("{:" + str(agent_name_length) + "}").format(agent_cls.__name__)

        leaderboard_line = ("{} | win_rate={:.4f} res_win_rate={:.4f} spy_win_rate={:.4f} | {}").format(
                            agent_name, win_rate, res_win_rate, spy_win_rate,
                            " ".join("{}={}".format(key, agent_scores[key]) for key in agent_scores))

        leaderboard.append((-win_rate, leaderboard_line))

    leaderboard.sort()
    leaderboard = leaderboard[:LEADERBOARD_LINES]

    print("\nLEADERBOARD AFTER {} GAMES".format(scores["games"]))
    print("Resistance Wins: {}, Spy Wins: {}, Resistance Win Rate: {:.4f}".format(scores["res_wins"], scores["spy_wins"], scores["res_wins"]/scores["games"]))
    for i, item in enumerate(leaderboard):
        _, line = item
        print("{:2}: {}".format(i+1, line)[:LEADERBOARD_WIDTH])

def calculate_and_print_target_agent_stats(scores):
    # Calculate average win rates and print stats for specific agents
    print("\n--- AVERAGE WIN RATES OF TARGET AGENTS ---")
    for target_agent in TARGET_AGENTS:
        for agent_cls in agent_classes:
            if agent_cls.__name__ == target_agent:
                agent_scores = scores[agent_cls]
                win_rate = agent_scores["wins"] / agent_scores["games"] if agent_scores["games"] else 0
                res_win_rate = agent_scores["res_wins"] / agent_scores["res"] if agent_scores["res"] else 0
                spy_win_rate = agent_scores["spy_wins"] / agent_scores["spy"] if agent_scores["spy"] else 0
                print(f"{target_agent}: win_rate={win_rate:.4f}, res_win_rate={res_win_rate:.4f}, spy_win_rate={spy_win_rate:.4f}")

def print_win_rate_differences(scores):
    # Print win rate differences between specific agents
    def get_win_rate(agent_name):
        for agent_cls in agent_classes:
            if agent_cls.__name__ == agent_name:
                agent_scores = scores[agent_cls]
                return agent_scores["wins"] / agent_scores["games"] if agent_scores["games"] else 0
        return 0

    hmm_win_rate = get_win_rate("HMM")
    satisfactory_win_rate = get_win_rate("SatisfactoryAgent")
    basic_win_rate = get_win_rate("BasicAgent")
    random_win_rate = get_win_rate("RandomAgent")

    print("\n--- WIN RATE DIFFERENCES ---")
    print(f"HMM vs SatisfactoryAgent: {hmm_win_rate - satisfactory_win_rate:.4f}")
    print(f"HMM vs BasicAgent: {hmm_win_rate - basic_win_rate:.4f}")
    print(f"HMM vs RandomAgent: {hmm_win_rate - random_win_rate:.4f}")

# Tournament and game logic
def run_tournament():
    scores = {agent_cls: {
        "errors": 0,
        "games": 0, "wins": 0, "losses": 0, "res": 0, "spy": 0,
        "res_wins": 0, "res_losses": 0, "spy_wins": 0, "spy_losses": 0,
        } for agent_cls in agent_classes}
    scores["games"] = 0
    scores["res_wins"] = 0
    scores["spy_wins"] = 0

    for game_num in range(NUMBER_OF_GAMES_PER_TOURNAMENT):
        number_of_players = random.randint(5, 10)
        agents = random.sample(agent_pool, number_of_players)

        game = Game(agents)
        game.play()

        # update the scores
        resistance_victory, winning_team, losing_team = game.get_results()

        # overall game stats
        scores["games"] += 1
        if resistance_victory:
            scores["res_wins"] += 1
        else:
            scores["spy_wins"] += 1

        # agent stats
        for agent in agents:
            agent_scores = scores[agent.orig_class]
            agent_scores["games"] += 1
            agent_scores["errors"] += agent.errors
            agent.reset_error_counter()

        for agent in winning_team:
            agent_scores = scores[agent.orig_class]
            agent_scores["wins"] += 1
            if resistance_victory:
                agent_scores["res"] += 1
                agent_scores["res_wins"] += 1
            else:
                agent_scores["spy"] += 1
                agent_scores["spy_wins"] += 1

        for agent in losing_team:
            agent_scores = scores[agent.orig_class]
            agent_scores["losses"] += 1
            if resistance_victory:
                agent_scores["spy"] += 1
                agent_scores["spy_losses"] += 1
            else:
                agent_scores["res"] += 1
                agent_scores["res_losses"] += 1

    print_leaderboard(scores)
    calculate_and_print_target_agent_stats(scores)
    print_win_rate_differences(scores)

# Plotting win rates
def plot_win_rates(win_rate_history):
    plt.figure(figsize=(10, 6))
    for agent, history in win_rate_history.items():
        plt.plot(history, label=agent)

    plt.xlabel('Tournament')
    plt.ylabel('Win Rate')
    plt.title('Win Rates Over Tournaments')
    plt.legend()
    plt.show()

# Main logic to run multiple tournaments
win_rate_history = {agent_cls.__name__: [] for agent_cls in agent_classes}

for tournament_num in range(NUMBER_OF_TOURNAMENTS):
    print(f"\n=== TOURNAMENT {tournament_num + 1} ===")
    run_tournament()

    for agent_cls in agent_classes:
        agent_scores = scores[agent_cls]
        win_rate = agent_scores["wins"] / agent_scores["games"] if agent_scores["games"] else 0
        win_rate_history[agent_cls.__name__].append(win_rate)

# Plot the win rate history
plot_win_rates(win_rate_history)
