from models.hand import PlayerHand
import unittest
from models.card import Card, Suit, Rank

class TestPlayerHand(unittest.TestCase):

    def setUp(self):
        self.ace_clubs = Card(Suit.Clubs, Rank.ACE)
        self.ace_hearts = Card(Suit.Hearts, Rank.ACE)
        self.king_spades = Card(Suit.Spades, Rank.KING)
        self.queen_diamonds = Card(Suit.Diamonds, Rank.QUEEN)
        self.ten_clubs = Card(Suit.Clubs, Rank.TEN)
        self.five_hearts = Card(Suit.Hearts, Rank.FIVE)
        self.two_spades = Card(Suit.Spades, Rank.TWO)
        self.seven_diamonds = Card(Suit.Diamonds, Rank.SEVEN)
        self.nine_clubs = Card(Suit.Clubs, Rank.NINE)
        self.king_hearts = Card(Suit.Hearts, Rank.KING) # For pair testing

    def test_player_hand_initialization(self):
        # Test valid initialization
        player_hand = PlayerHand([self.ace_clubs, self.king_spades], 100)
        self.assertEqual(player_hand.bet, 100)
        self.assertFalse(player_hand.doubled)
        self.assertEqual(player_hand.points, 21)

        # Test invalid bet amount
        with self.assertRaises(ValueError):
            PlayerHand([self.five_hearts, self.two_spades], -50)
        with self.assertRaises(ValueError):
            PlayerHand([self.five_hearts, self.two_spades], "abc")

    def test_bet_property(self):
        player_hand = PlayerHand([self.five_hearts, self.two_spades], 50)
        self.assertEqual(player_hand.bet, 50)

    def test_doubled_property(self):
        player_hand = PlayerHand([self.five_hearts, self.two_spades], 50)
        self.assertFalse(player_hand.doubled)
        player_hand.mark_as_doubled()
        self.assertTrue(player_hand.doubled)

    def test_add_bet(self):
        player_hand = PlayerHand([self.five_hearts, self.two_spades], 50)
        player_hand.add_bet(25)
        self.assertEqual(player_hand.bet, 75)
        player_hand.add_bet(0) # Adding zero should not change bet
        self.assertEqual(player_hand.bet, 75)

        with self.assertRaises(ValueError):
            player_hand.add_bet(-10) # Cannot add negative bet
        with self.assertRaises(ValueError):
            player_hand.add_bet("invalid")

    def test_mark_as_doubled(self):
        player_hand = PlayerHand([self.five_hearts, self.two_spades], 50)
        self.assertFalse(player_hand.doubled)
        player_hand.mark_as_doubled()
        self.assertTrue(player_hand.doubled)
        player_hand.mark_as_doubled() # Calling again should not change anything
        self.assertTrue(player_hand.doubled)

    def test_has_pair(self):
        # True cases
        pair_hand1 = PlayerHand([self.king_spades, self.king_hearts], 10)
        self.assertTrue(pair_hand1.has_pair())

        pair_hand2 = PlayerHand([self.ace_clubs, self.ace_hearts], 10)
        self.assertTrue(pair_hand2.has_pair())

        # True cases (different ranks, but same point value)
        no_pair_hand1 = PlayerHand([self.king_spades, self.queen_diamonds], 10)
        self.assertTrue(no_pair_hand1.has_pair())

        # False cases (more than 2 cards)
        no_pair_hand2 = PlayerHand([self.king_spades, self.king_hearts], 10)
        no_pair_hand2.add_card(self.five_hearts)
        self.assertFalse(no_pair_hand2.has_pair()) # Should be false as it's not a two-card hand anymore

        # False cases (less than 2 cards)
        no_pair_hand3 = PlayerHand([self.king_spades], 10)
        self.assertFalse(no_pair_hand3.has_pair())

    def test_split(self):
        # Valid split
        original_bet = 50
        pair_hand = PlayerHand([self.king_spades, self.king_hearts], original_bet)
        self.assertTrue(pair_hand.has_pair())
        self.assertEqual(len(pair_hand.cards), 2)

        new_hand = pair_hand.split()

        # Check original hand after split
        self.assertEqual(len(pair_hand.cards), 1)
        self.assertEqual(pair_hand.cards[0], self.king_spades)
        self.assertEqual(pair_hand.bet, original_bet) # Bet remains the same for original hand

        # Check new hand
        self.assertIsInstance(new_hand, PlayerHand)
        self.assertEqual(len(new_hand.cards), 1)
        self.assertEqual(new_hand.cards[0], self.king_hearts)
        self.assertEqual(new_hand.bet, original_bet) # New hand gets the same bet amount

        # Test invalid split (no pair)
        no_pair_hand = PlayerHand([self.king_spades, self.nine_clubs], 10)
        self.assertFalse(no_pair_hand.has_pair())
        with self.assertRaises(ValueError):
            no_pair_hand.split()

        # Test invalid split (more than 2 cards)
        multi_card_hand = PlayerHand([self.king_spades, self.king_hearts], 10)
        multi_card_hand.add_card(self.five_hearts)
        self.assertFalse(multi_card_hand.has_pair()) # has_pair checks for exactly 2 cards
        with self.assertRaises(ValueError):
            multi_card_hand.split()

        # Test invalid split (less than 2 cards)
        single_card_hand = PlayerHand([self.king_spades], 10)
        self.assertFalse(single_card_hand.has_pair())
        with self.assertRaises(ValueError):
            single_card_hand.split()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)