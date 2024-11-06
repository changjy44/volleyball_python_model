import json
import random

class Player:
  def __init__(self, player_data, verbose):
    self.verbose = verbose

    self.name = player_data[0]
    self.team = player_data[1]
    self.role = player_data[2]

    self.att_err_perc = player_data[27]
    self.att_kill_perc = player_data[28]
    self.att_perc = player_data[29]

    self.svc_err_perc = player_data[33]
    self.svc_ace_perc = player_data[34]
    self.svc_perc = player_data[35]

  def validate_player(self):
    pass

  def play_service(self):
    rnd = random.random()
    if rnd < self.svc_err_perc: # Error

      print(f"Player {self.name} ({self.team}, {self.role}) service error") if self.verbose else ""
      return 2
    elif rnd < self.svc_err_perc + self.svc_ace_perc: # Ace

      print(f"Player {self.name} ({self.team}, {self.role}) service ace") if self.verbose else ""
      return 1
    else:

      print(f"Player {self.name} ({self.team}, {self.role}) service attempt") if self.verbose else ""
      return 0

  def play_spike(self):
    rnd = random.random()
    if rnd < self.att_err_perc: # Error

      print(f"Player {self.name} ({self.team}, {self.role}) spike error") if self.verbose else ""

      return 2 
    elif rnd < self.att_err_perc + self.att_kill_perc: # Kill

      print(f"Player {self.name} ({self.team}, {self.role}) spike kill") if self.verbose else ""
      return 1
    else:

      print(f"Player {self.name} ({self.team}, {self.role}) spike attempt") if self.verbose else ""
      return 0

class Team:
  def __init__(self, team_name, team_data, verbose):
    self.verbose = verbose

    self.team_name = team_name
    self.OH_perc = team_data["OH_perc"]
    self.MB_perc = team_data["MB_perc"]
    self.O_perc = team_data["O_perc"]

    self.oh1_player = Player(team_data["OH"][0], verbose)
    self.oh2_player = Player(team_data["OH"][1], verbose)
    self.mb1_player = Player(team_data["MB"][0], verbose)
    self.mb2_player = Player(team_data["MB"][1], verbose)
    self.o_player = Player(team_data["O"][0], verbose)    
    self.s_player = Player(team_data["S"][0], verbose)    
    self.l_player = Player(team_data["L"][0], verbose)

    self.initialize_rotation()

  def play_service(self):
    return self.players[3].play_service()

  def play_spike(self):
    rnd = random.random()
    if rnd < self.OH_perc:

      print(f"Team {self.team_name} set to OH") if self.verbose else ""
      return self.curr_oh.play_spike()
    elif rnd < self.OH_perc + self.MB_perc:

      print(f"Team {self.team_name} set to MB") if self.verbose else ""
      return self.curr_mb.play_spike()
    else:

      print(f"Team {self.team_name} set to O") if self.verbose else ""
      return self.curr_o.play_spike()
    
  def rotate(self):
    temp = self.players[0]
    self.players[0] = self.players[5]
    self.players[5] = self.players[4]
    self.players[4] = self.players[3]
    self.players[3] = self.players[2]
    self.players[2] = self.players[1]
    self.players[1] = temp
    
    if self.players[0].role == 'L':
      print(f"Team {self.team_name} sub Libero out") if self.verbose else ""

      lib_player = self.players[0]
      mb_player = self.out_player
      self.players[0] = mb_player # sub MB in
      self.curr_mb = mb_player
      self.out_player = lib_player
    elif self.players[0].role == 'OH':
      self.curr_oh = self.players[0]

  def check_libero(self):
    if self.players[3].role == 'MB':

      print(f"Team {self.team_name} sub MB out") if self.verbose else ""
      mb_player = self.players[3]
      self.players[3] = self.out_player
      self.out_player = mb_player

  def initialize_rotation(self):
    self.players = [
      self.oh1_player,
      self.mb1_player,
      self.s_player,
      self.oh2_player,
      self.l_player,
      self.o_player
    ]

    self.out_player = self.mb2_player

    self.curr_oh = self.oh1_player
    self.curr_mb = self.mb1_player
    self.curr_o = self.o_player

class Simulator:
  def __init__(self, teamA, teamB, match_data, verbose):
    self.verbose = verbose
    self.set_number = 1

    self.sets = [0, 0]
    self.scores = [0, 0]
    self.turn = 0 # team A serve first

    teamA_data = match_data[teamA]
    teamB_data = match_data[teamB]
    teamA = Team(teamA, teamA_data, verbose)
    teamB = Team(teamB, teamB_data, verbose)

    self.teams = [teamA, teamB]
    self.score_log = []

  def simulate(self):
    while self.sets[0] < 3 and self.sets[1] < 3:
      self.simulate_set()

  def simulate_set(self):
    # Team A serve first, then team B
    self.turn = self.set_number % 1
    print(f"Starting set number {self.set_number}") if self.verbose else ""
    while not self.check_win():
      # Sub MB with libero
      serve_team = self.turn

      self.teams[1 - self.turn].check_libero()

      serve_outcome = self.teams[self.turn].play_service()
      if serve_outcome == 0: # Attempt
        self.turn = 1 - self.turn 

        while True:
          spike_outcome = self.teams[self.turn].play_spike()
          if spike_outcome == 0: # Attempt
            self.turn = 1 - self.turn 

          elif spike_outcome == 1: # Kill
            self.win_rally(self.turn, serve_team)
            break

          elif spike_outcome == 2: # Error
            self.win_rally(1 - self.turn, serve_team)
            break

          else:
            raise Exception("undefined case")

      elif serve_outcome == 1: # Ace
        self.win_rally(self.turn, serve_team)

      elif serve_outcome == 2: # Error
        self.win_rally(1 - self.turn, serve_team)

      else:
        raise Exception("undefined case")
    
    self.set_number += 1
    self.score_log.append(self.scores)
    self.scores = [0, 0]
    self.teams[0].initialize_rotation()
    self.teams[1].initialize_rotation()

  def win_rally(self, team, serve_team):
    self.scores[team] += 1
    self.turn = team
    if team != serve_team:
      self.teams[team].rotate()

  def check_win(self):
    if (self.set_number == 5):
      if self.scores[0] == 15:
        self.sets[0] += 1
        return True
      elif self.scores[1] == 15:
        self.sets[1] += 1
        return True
      else:
        return False
      
    elif (self.set_number >= 1 and self.set_number <= 4):
      if self.scores[0] == 25:
        self.sets[0] += 1
        return True
      elif self.scores[1] == 25:
        self.sets[1] += 1
        return True
      else:
        return False
    else:
      raise Exception("exceed set_number case")
    
  def get_winner(self):
    if self.sets[0] == 3:
      return self.teams[0].team_name
    else:
      return self.teams[1].team_name

  def print_result(self):
    print(f"Result ({self.teams[0].team_name} vs {self.teams[1].team_name})")
    print(f"Sets {self.sets}")
    print(f"Score {self.score_log}")


if __name__ == "__main__":
  with open('2023-vnl-team-data.json') as f:
    matches_2023 = json.load(f)

  with open('2024-vnl-data.json') as f:
    matches_2024 = json.load(f)


  prediction_rate_array = []

  for count in range(1):
    games = []
    matches_predicted_correctly = 0
    total_matches = 0

    for match in matches_2024:
      teamA = match['teamA']
      teamB = match['teamB']
      teamA_score = match['teamA_score']
      teamB_score = match['teamB_score']
      teamA_wins_result = teamA_score > teamB_score

      if teamA not in matches_2023 or teamB not in matches_2023:
        continue

      teamA_wins = 0
      teamB_wins = 0
      teamA_wins_predicted = True
      for i in range(31):
        simulator = Simulator(teamA, teamB, matches_2023, False)
        simulator.simulate()
        if simulator.get_winner() == teamA:
          teamA_wins += 1
        else:
          teamB_wins += 1

      if teamA_wins > teamB_wins:
        teamA_wins_predicted = True
      else:
        teamA_wins_predicted = False
      
      total_matches += 1
      if teamA_wins_result == teamA_wins_predicted:
        matches_predicted_correctly += 1

      data = [teamA, teamB, teamA_score, teamB_score, teamA_wins, teamB_wins]
      print(data)
      games.append(data)

    print(f"Prediction result: {matches_predicted_correctly}/{total_matches}")
    print(f"Prediction rate: {matches_predicted_correctly/total_matches}")
    prediction_rate_array.append(matches_predicted_correctly/total_matches)
  
  print(f"Final prediction rate across 3 runs {sum(prediction_rate_array)/len(prediction_rate_array)}")