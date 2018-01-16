#!/usr/bin/env python3


from random import shuffle


class Game:

    def __init__(self, playername, decks):
        # Below line is used primarily for results output, but can be expanded later for saving games.
        self.currentround = 1
        self.player = Player(playername)
        self.dealer = Player("Dealer")
        self.deck = Deck(decks)  # Initializes the decks, taking 'decks' as the number of decks to use.
        self.allplayers = [self.dealer, self.player]  # Sets up a list of players to be able to iterate through them.
        self.over = False  # Game is over when the player is out of money.

    def new_round(self):
        # In a real game the deck wouldn't be shuffled every round. However, introducing shuffling only occasionally
        # introduces more complexity than will be noticeable in the game.
        self.currentround += 1
        self.deck.shuffle()
        for player in self.allplayers:
            player.hands.append(Hand())  # Instantiates a new hand for both the player and dealer and gives them cards
            for x in range(2):
                newcard = self.deck.deal_card()
                player.hands[0].cards.append(newcard)
                if x == 1:
                    player.hands[0].calculate_value()

    def player_actions(self, hand, action="stand"):
        if action == "hit" or action == "double":
            hand.cards.append(self.deck.deal_card())
            hand.calculate_value()
            if hand.bust:
                hand.actions_taken.append("stand")
        if action == "double":
            hand.actions_taken.append(action)
            self.player.bet += self.player.bet*2
        if action == "split":
            # Giving a new hand, splitting the cards from the old hand and dealing a new card to each
            self.player.hands.append(Hand(2))
            self.player.hands[1].cards.append(hand.cards[-1])
            hand.cards.pop(-1)
            for hands in self.player.hands:
                hands.cards.append(self.deck.deal_card())
                hands.calculate_value()
            hand.actions_taken.append(action)
        if action == "stand":
            hand.actions_taken.append(action)

    def player_done(self):
        # Check if each hand is stood
        if all(hand.check_actions("stand") for hand in self.player.hands):
            return True
        else:
            return False

    def check_winner(self):
        # This goes through all players except the dealer to see if they win.
        # Doing it this way to render this expandable for multiple players, even though only one is implemented so far.
        win_values = {0: "lose", 1: "win", 2: "push"}
        win_messages = []
        # Check if the player has won or not
        for player in self.allplayers[1:]:
            result = player.check_winner(self.dealer.hands[0])
            win_messages.append(win_values[result])
            if result == 1:
                player.bank += player.bet * 2
        return win_messages

    def end_round(self):
        # End round cleanup
        # todo: Create logging function to record gameplay
        for player in self.allplayers:
            for hand in player.hands:
                self.deck.shoe.extend(hand.cards)
                del hand
            player.hands.clear()
            player.bet = 0
        if self.player.bank <= 0:
            self.game_over()

    def game_over(self):
        # todo: Extend with end of game logging
        self.over = True

class Player:

    def __init__(self, name, bank=50):
        self.name = name
        self.bet = 0
        self.hands = []  # These are the hands that the player has.
        self.bank = bank  # The amount of money they start with. Eventually "bank" should be adjustable per-game.
        self.hand_held = 0  # This is used to determine which hand the player is looking at, after splitting

    def place_bet(self, player_bet):
        self.bet = player_bet
        self.bank -= player_bet

    def __str__(self):
        return self.name

    def look_at_hand(self, hand):
        # TODO: Evaluate -- do I need this method?
        # Prints the hands for play when running the script; else, returns the cards in hand (for eventual UI)
        if __name__ == '__main__':
            hand_value = "\nValue: " + str(hand.value) + "\n"
            return hand_value + "\n".join(map(str, hand.cards[:]))

        else:
            return hand.cards[:]

    def switch_hands(self):  # Pick up a different hand (when hands are split)
        if self.hand_held == 0:
            self.hand_held = 1
        else:
            self.hand_held = 0

    def double_check(self):
        # This will do nothing but check whether or not a double is legal
        if self.bet * 2 <= self.bank:
            return True
        else:
            return False

    def check_winner(self, dealer):
        # Takes the dealer's hand as input
        # 0 == Loss
        # 1 == Win
        # 2 == Push (loss, but used separately for recording/printing values).
        winning_hand = None
        for hand in self.hands:
            if not hand.bust and hand.value == max(hands.value for hands in self.hands):
                winning_hand = hand
        if not winning_hand:
            return 0  # If winning_hand isn't set, all hands were bust. Therefore, loss.
        elif dealer.bust or winning_hand.value > dealer.value:
            return 1  # If the dealer went bust or if player hand is higher than the dealer's hand, win.
        elif dealer.value == winning_hand.value:
            return 2  # Player pushes if neither went bust and player didn't win
        else:
            return 0  # All other permutations result in the player losing their bet and not pushing.


class Hand:
    """This holds values of the current cards. This will be deleted once a round is wrapped up and instantiated again
    when the round begins."""

    def __init__(self, name=1):
        self.name = name  # The "name" is hand 1 or 2. Probably a clunky way to use this.
        self.cards = []  # This holds Card objects
        self.value = 0
        self.bust = False  # Makes the hand bust if its value is over 21
        self.pair = False  # A "pair" are two cards of the same value (gotten from calculate_value)
        self.blackjack = False
        self.actions_taken = []  # The once-only actions the hand has taken this round (double, hit, stand).

    def calculate_value(self):
        self.value = sum([cards.value for cards in self.cards])
        if any(cards.rank == 1 for cards in self.cards) and self.value + 10 <= 21:
            self.value += 10  # If hand.value would be less than 21, makes aces worth 11 instead of 1.
        if self.value > 21:
            self.bust = True
        if len(self.cards) == 2:
            if any(cards.value == 10 for cards in self.cards) and any(cards.rank == 1 for cards in self.cards):
                self.blackjack = True
            if self.cards[0].value == self.cards[1].value:
                self.pair = True
        return self.value

    def check_actions(self, action=None):
        # Returns the length of actions_taken if no action is passed to it.
        if not action:
            return len(self.actions_taken)
        else:  # Determines if the action specified has already been taken
            if action in self.actions_taken:
                return True
            else:
                return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "hand" + str(self.name).title()  # Gives the hand a name. Using "hand" may be dumb.


class Deck:
    """Creating a deck object. This is more accurately conceptualized as multiple decks -- however, since all the decks
    are shuffled together to create a single set of cards, it is in essence just one big mega-deck."""

    def __init__(self, num_decks):
        self.cards = []
        self.shoe = []  # Cards that have already been played.
        for deck in range(num_decks):  # For the number of decks specified, add all the cards.
            self.cards += (Card(rank, suit) for rank in range(1, 14) for suit in 'chsd')
            # chsd = list for suits (clubs, hearts, spades, diamonds).

    def shuffle(self):
        #  Shuffles the deck. This is called in Game.new_round
        shuffle(self.cards)

    def deal_card(self):
        if not len(self.cards):  # If the deck doesn't have enough cards left, then reshuffle
            self.cards.extend(self.shoe)
            self.shuffle()
            self.shoe.clear()
        newcard = self.cards[-1]
        self.cards.pop()
        return newcard


class Card:
    suits = {'c': 'Clubs', 'h': 'Hearts', 's': 'Spades', 'd': 'Diamonds'}
    ranks = {1: 'Ace', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine',
             10: 'Ten', 11: 'Jack', 12: 'Queen', 13: 'King'}

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.value = rank if rank < 11 else 10  # Setting card value. Face cards (rank 11-13) are worth 10.

    def __repr__(self):
        return self.__str__()
        # Insures that when printing a card, the card is printed as a string and not an object reference. See __str__

    def __str__(self):
        # Whenever this object is printed, print the card name.
        return "%s of %s" % (Card.ranks[self.rank], Card.suits[self.suit])


def play_game():
    """This function should only be run when playing this from the command line."""
    # TODO: Replace game with variables once out oftesting and ready for command line release
    game = Game('Bob', 2)
    while True:
        print("Round ", game.currentround)  # Printing the round beginning.
        game.new_round()
        dealer = game.dealer.hands[0]  # Simplify dealer's hand for readability
        game.player.place_bet(get_bet(game.player.bank))
        print("\nDealer has the", dealer.cards[1], "showing.")  # Prints the dealer's face-up card
        play_hands(game, game.player)
        dealer_actions(game, game.dealer, dealer)
        print("You " + " ".join(game.check_winner()) + ".\nNew bank: ", game.player.bank)
        if input("Press Y to continue or anything else to quit.") not in ("y", "Y"):
            quit(0)
        game.end_round()
        if game.over:
            break
    print("You're out of money -- game over! You lasted " + str(game.currentround - 1) + " rounds.")


def play_hands(game, player):
    # Until you Stand or go bust (see player_actions), you will be prompted to take action.
    current_hand = player.hands[player.hand_held]  # Simplifying accessing the current hand as an object and not int
    print(player.look_at_hand(current_hand), "\n")
    action = get_action(player, current_hand)  # Gets from the player what they want to do with the held hand
    if action == "switch":  # Allows player to switch hands, assuming they have previously split hands.
        player.switch_hands()
        print(player.look_at_hand(current_hand), "\n")
    else:
        game.player_actions(current_hand, action)  # Does the specified action, if it wasn't "switch" or quit.
        print(player.look_at_hand(current_hand), "\n")
    if current_hand.check_actions("stand"):  # If they stood, then the hand is maybe over...
        if not game.player_done():  # ... unless not ALL hands have been stood. In which case, switch to other hand.
            player.switch_hands()
        else:
            return  # If they're all done, then exit this function.
    play_hands(game, player)  # If we haven't stood yet, then continue prompting for action on this hand.


def dealer_actions(game, player, hand):
    spacer = "\n" + "*"*30 + "\n"
    print(spacer + "Dealer reveals:\n", player.look_at_hand(hand))
    while hand.value < 16:
        game.player_actions(hand, "hit")
    print("\nDealer's final hand: ", player.look_at_hand(hand), spacer)


def get_bet(bank):
    # todo fold checks into place_bet function
    while True:  # Getting the player's bet. This will only accept numbers, and not more than the player's bank.
        entered_bet = input("Place your bet, max " + str(bank) + ":  (Press Q to quit)")
        if entered_bet in ("q", "Q"):
            quit(0)
        try:
            bet = int(entered_bet)
            if bet <= 0:
                raise ValueError
        except ValueError:
            print("Invalid bet. Bet must be a number between 1 and" + str(bank) + "!")
            continue
        if bet > bank:
            print("Can't bet more than you have!")
            continue
        else:
            break
    return bet


def get_action(player, hand):
    # This is retrieving an action from the player (text only).
    possible_actions = ["stand", "hit"]
    if not hand.check_actions("double") and player.double_check():
        possible_actions.append("double")
    if not hand.check_actions("split") and hand.name == 1 and hand.pair:
        possible_actions.append("split")
    print("You are holding hand " + str(hand.name) + ". Choose an action or press 'S' to switch hands, 'Q' to quit.\n")
    for option in possible_actions:
        print(possible_actions.index(option), ")", option.title())
    action = None
    try:
        selected_action = input("\nEnter 0-" + str(len(possible_actions)-1) + ": ")
        if selected_action in ("q", "Q"):
            quit(0)
        elif selected_action in ("s", "S"):
            return "switch"
        action = possible_actions[int(selected_action)]
    except IndexError:
        print("Not an option. Please try again.")
    hand.actions_taken.append(action)
    return action


if __name__ == '__main__':
    play_game()
