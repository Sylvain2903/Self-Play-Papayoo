from gym import Env
from gym.spaces import Discrete, Box
import random as rand
import numpy as np
from stable_baselines import logger
from .classes import *

class PapayooEnv(Env):

    def __init__(self, verbose=False, manual=False):
        super(PapayooEnv, self).__init__()
        self.name = 'papayoo'
        self.manual = manual
        self.verbose = verbose

        self.n_players = 4
        self.dealer = -1  # so that first dealer is 0
        # Make four players
        self.players = [Player(i) for i in range(self.n_players)]
        '''
        Player physical locations:
        Game runs clockwise

            p2
        p1        p3
            p0

        '''
        self.sorted_deck = Deck()
        self.sorted_deck.sort()
        self.space_shape = (4*60+6, )
        self.observation_space = Box(-1, 1, self.space_shape)
        self.action_space = Discrete(60)

    @property
    def observation(self):
        event = []
        if self.passing:
            event = np.array([1, 0])
            hand = np.array([-self.current_player.hand.contains_card(card) for card in self.sorted_deck.deck])
        else:
            event = np.array([0, 1])
            hand = np.array([self.current_player.hand.contains_card(card) for card in self.sorted_deck.deck])
        played = np.array([self.card_played(card) for card in self.sorted_deck.deck])
        collected = np.array([self.current_player.collected_card(card) for card in self.sorted_deck.deck])
        trick = np.array([self.card_in_trick(card) for card in self.sorted_deck.deck])
        payoo_obs = [0]*4
        if self.suit_papayoo != Suit(-1):
            payoo_obs[self.suit_papayoo.iden-1] = 1
        payoo_arr = np.array(payoo_obs)
        obs = np.concatenate((event, hand, played-2*collected, trick, payoo_arr))
        out = np.append(obs, self.legal_actions)
        return out

    @property
    def legal_actions(self):
        if self.current_player.hand.has_suit(self.current_trick.suit):
            legal_actions = []
            for card in self.sorted_deck.deck:
                if card.suit == self.current_trick.suit:
                    legal_actions.append(self.current_player.hand.contains_card(card))
                else:
                    legal_actions.append(0)
        else:
            legal_actions = [self.current_player.hand.contains_card(card) for card in self.sorted_deck.deck]
        return np.array(legal_actions)

    @property
    def current_player(self):
        return self.players[self.current_player_num]

    def deal_cards(self):
        i = 0
        while self.deck.size() > 0:
            self.players[i % len(self.players)].add_card(self.deck.deal())
            i += 1

    def passed_cards_to_string(self):
        string_arr = ['', '', '', '']
        for i, list in enumerate(self.passed_cards):
            string = ''
            for card in list:
                 string += card.__str__() + ' '
            string_arr[i] = string
        return string_arr.__str__()

    def card_played(self, card):
        for c in self.cards_played:
            if c.__eq__(card):
                return 1
        return 0

    def card_in_trick(self, card):
        for c in self.current_trick.trick:
            if c == card:
                return 1
        return 0

    def action_to_card(self, action):
        card = self.sorted_deck.deck[action]
        return card

    def calculate_trick_score(self):
        score = 0
        for card in self.current_trick.trick:
            if card == Card(7, self.suit_papayoo.iden):
                score += 40
            elif card.suit == Suit(0):
                score += card.rank.rank
        return score

    def score_game(self):
        reward = [0.0] * self.n_players
        scores = [p.score for p in self.players]
        scores.sort()
        positions = [[], [], [], []]
        for p in self.players:
            for i, score in enumerate(scores):
                if p.score == score:
                    positions[i].append(p.index)

        for i, position in enumerate(positions):
            for index in position:
                if i == 0:
                    reward[index] += 1.0 / len(position)
                if i == 1:
                    reward[index] += 0.5 / len(position)
                if i == 2:
                    reward[index] += -0.5 / len(position)
                if i == 3:
                    reward[index] += -1.0 / len(position)
        return reward

    def step(self, action):
        reward = [0] * self.n_players
        done = False

        card = self.action_to_card(action)
        self.current_player.remove_card(card)

        if self.passing:
            self.passed_cards[self.current_player_num].append(card)
            if len(sum(self.passed_cards, [])) == 12:
                for i,l in enumerate(self.passed_cards):
                    for card in l:
                        self.players[(i+1) % self.n_players].add_card(card)
                logger.debug(f' --- Playing ---')
                self.passing = False
                self.suit_papayoo = Suit(rand.randint(1,4))
                logger.debug(f'Suit Papayoo: {self.suit_papayoo}')
        else:
            self.current_trick.add_card(card, self.current_player_num)

        # Check if trick is over
        if self.current_trick.num_cards_in_trick == self.n_players:
            score = self.calculate_trick_score()
            self.current_player_num = self.current_trick.winner
            self.current_player.score += score
            self.current_player.cards_collected.extend(self.current_trick.trick)
            self.cards_played.extend(self.current_trick.trick)
            self.trick_num += 1
            if self.trick_num == 15:
                reward = self.score_game()
                done = True
                self.done = True
            else:
                logger.debug(f"Cards on table: {self.current_trick.__str__()}")
                self.current_trick.reset()
        else:
            self.current_player_num = (self.current_player_num+1) % self.n_players

        return self.observation, reward, done, {}

    def reset(self):
        logger.debug(f'\n\n---- NEW GAME PAPAYOO ----')
        # Generate a full deck of cards, shuffle and distribute it
        for p in self.players:
            p.reset()
        self.deck = Deck()
        self.deck.shuffle()
        self.dealer = (self.dealer + 1) % self.n_players
        self.deal_cards()
        self.current_player_num = self.dealer
        self.current_trick = Trick()
        self.trick_num = 0
        self.cards_played = []
        self.done = False
        self.suit_papayoo = Suit(-1) # Unset
        logger.debug(f'--- Passing Cards ---')
        self.passing = True
        if not self.passing:
            self.suit_papayoo = Suit(rand.randint(1,4))
            logger.debug(f'Suit Papayoo: {self.suit_papayoo}')
        self.passed_cards = [[], [], [], []]
        out = self.observation
        return out
                
    def render(self, mode='human', close=False):
        logger.debug('')
        if close:
            return
        if self.done:
            logger.debug(f'GAME OVER')
            logger.debug(f'Scores: {[self.players[i].score for i in range(4)]}')
        else:
            logger.debug(f"It is Player {self.current_player.index}'s turn to move")
            logger.debug(f"Current hand: {self.current_player.hand}")

        logger.debug(f"Passed cards: {self.passed_cards_to_string()}")
        logger.debug(f"Cards on table: {self.current_trick.__str__()}")

        if self.verbose:
            logger.debug(f'\nObservation: \n{self.observation}')

        if not self.done:
            logger.debug(f'\nLegal actions: {[i for i,o in enumerate(self.legal_actions) if o != 0]}')
