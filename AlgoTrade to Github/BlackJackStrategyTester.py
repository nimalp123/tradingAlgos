from ctypes import string_at
import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        ranks = [str(n) for n in range(2, 11)] + list('JQKA')
        suits = 'spades diamonds clubs hearts'.split()
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks] * 8
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()
stringP = ""
def hand_value(hand):
    value = sum(card.value() for card in hand)
    aces = sum(card.rank == 'A' for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def play_round(deck, stringP):
    player_hand = [deck.deal(), deck.deal()]
    dealer_hand = [deck.deal(), deck.deal()]

    # Player's turn
    while hand_value(player_hand) < 17:
        player_hand.append(deck.deal())

    # Dealer's turn
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.deal())

    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)
    stringP = stringP + ("\n" + str(player_value) + "  "+ str(dealer_value))
    if player_value > 21:
        return 'Lose', stringP
    elif dealer_value > 21 or player_value > dealer_value:
        return 'Win', stringP
    elif player_value < dealer_value:
        return 'Lose', stringP
    else:
        return 'Draw', stringP

def simulate_rounds(num_rounds, stringPlE):
    deck = Deck()
    results = {'Win': 0, 'Lose': 0, 'Draw': 0}
    for _ in range(num_rounds):
        result, stringPl = play_round(deck, stringP)
        stringPlE += stringPl
        results[result] += 1
        if len(deck.cards) < 20:
            deck = Deck()  # Reshuffle
    return results, stringPlE

# Simulate 1000 rounds
rounds = 1000000
stringPlE = ""
results, stringP = simulate_rounds(rounds, stringPlE)
win_rate = results['Win'] / rounds
print(f'Win rate over {rounds} rounds: {win_rate:.4f}')
print(stringP)
print(f'Win rate over {rounds} rounds: {win_rate:.4f}')
wRa = pow(win_rate, 32)
print(f'liklihood to win 32 times in a row: {wRa}')

# deck composition is 8 standard decks
# dealer rules:
# The dealer can't make bets.
# The dealer must count their ace as 11.
# The dealer is the last to reveal their second card.
# The dealer hits on 16 and below and stands on 17 and above.
# The dealer can only flip their face-down card after all players have finished their turns.
# Player Strategy:
# Your Hand is 11 or Less: Always hit. There's no risk of busting, and you have a chance to improve your hand.

# Your Hand is Hard 12 to 16:

# If the dealer's upcard is 2 through 6, stand. The dealer has a higher chance of busting.
# If the dealer's upcard is 7 through Ace, hit. The dealer has a good chance of having a strong hand.
# Your Hand is 17 or Higher: Always stand. The risk of busting is high, and your hand is already strong.

# Soft Hands (Hands with an Ace counted as 11):

# If you have a soft 17 or less, hit. You can't bust by hitting, and you might improve your hand.
# If you have a soft 18 or more, stand.
# Pairs:

# Always split Aces and 8s.
# Never split 10s and 5s.
# For other pairs, follow the same rules as for hard hands.
# Doubling Down:

# Consider doubling down if your hand totals 10 or 11, especially if the dealer's upcard is lower.
# Insurance and Surrender:

# Avoid taking insurance.
# Surrender is not commonly offered, but if it is and you have a hard 16 and the dealer shows a 9, 10, or Ace, you might consider it.
# ChatGPT
# Given the detailed rules and strategy you've provided, we can make some general observations about the probability of winning a single hand in Blackjack, but calculating an exact probability is still complex and typically requires computer simulations. However, I can outline the factors that would be considered in such a calculation:

# Deck Composition: With 8 standard decks, the initial probabilities of drawing any specific card are known. This affects the likelihood of getting certain hands.

# Dealer Rules:

# The dealer hitting on 16 and below and standing on 17 and above is standard.
# The dealer counting their ace as 11 can affect the game, especially in determining when the dealer has a blackjack or a strong hand.
# Player Strategy:

# Your strategy for hard hands, soft hands, and pairs is a simplified version of the basic strategy and will influence the outcomes.
# Decisions on when to hit, stand, double down, and split pairs are crucial.
# Calculating Probabilities:

# For each player hand and dealer upcard, calculate the probabilities of various outcomes (win, lose, tie).
# Consider the likelihood of busting for both the player and the dealer.
# Factor in the probabilities of improving the hand when hitting or splitting.
# Simulation:

# Run simulations of thousands of hands using the given rules and strategy to estimate the win rate.
# Each simulation would track the outcome (win, lose, tie) and adjust for the changing composition of the deck.
# General Expectations:

# Under typical conditions with basic strategy, the house edge in Blackjack can be as low as 0.5%.
# With your simplified strategy, the house edge might be slightly higher, but the probability of winning a hand should still be close to 50%.
# Special Considerations:

# The rule about the dealer counting their ace as 11 might slightly alter the standard probabilities.
# The effectiveness of doubling down and splitting in your strategy will also impact the overall win rate.