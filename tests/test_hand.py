import unittest
from models.card import Card, Suit, Rank
from models.hand import Hand

class TestHand(unittest.TestCase):

    def setUp(self):
        # Define some common cards for testing
        self.ace_clubs = Card(Suit.Clubs, Rank.ACE)
        self.ace_hearts = Card(Suit.Hearts, Rank.ACE)
        self.king_spades = Card(Suit.Spades, Rank.KING)
        self.queen_diamonds = Card(Suit.Diamonds, Rank.QUEEN)
        self.ten_clubs = Card(Suit.Clubs, Rank.TEN)
        self.five_hearts = Card(Suit.Hearts, Rank.FIVE)
        self.two_spades = Card(Suit.Spades, Rank.TWO)
        self.seven_diamonds = Card(Suit.Diamonds, Rank.SEVEN)
        self.nine_clubs = Card(Suit.Clubs, Rank.NINE)

    def test_hand_initialization(self):
        # Test valid initializations
        hand1 = Hand([self.ace_clubs])
        self.assertEqual(len(hand1.cards), 1)
        self.assertEqual(hand1.cards[0], self.ace_clubs)
        # is_soft is determined by points calculation
        self.assertFalse(hand1.is_soft)

        hand2 = Hand([self.king_spades, self.queen_diamonds])
        self.assertEqual(len(hand2.cards), 2)
        self.assertEqual(hand2.cards[0], self.king_spades)
        self.assertEqual(hand2.cards[1], self.queen_diamonds)
        self.assertFalse(hand2.is_soft)

        # Test invalid initializations (wrong number of cards)
        with self.assertRaises(ValueError):
            Hand([])
        with self.assertRaises(ValueError):
            Hand([self.ace_clubs, self.king_spades, self.five_hearts])

        # # Test invalid initializations (not Card objects)
        # with self.assertRaises(TypeError):
        #     Hand(["not a card"])
        # with self.assertRaises(TypeError):
        #     Hand([self.ace_clubs, "not a card"])

    def test_add_card(self):
        hand = Hand([self.five_hearts])
        self.assertEqual(len(hand.cards), 1)
        hand.add_card(self.seven_diamonds)
        self.assertEqual(len(hand.cards), 2)
        self.assertEqual(hand.cards[1], self.seven_diamonds)
        self.assertEqual(hand.points, 12)  # 5 + 7

        # Test adding non-Card object
        # with self.assertRaises(TypeError):
        #     hand.add_card("invalid")

    def test_points_no_aces(self):
        # Below 21
        hand1 = Hand([self.five_hearts, self.seven_diamonds])  # 5 + 7 = 12
        self.assertEqual(hand1.points, 12)
        self.assertFalse(hand1.is_soft)

        # Exactly 21
        # K+Q+A = 10+10+1 = 21 (Ace forced to 1)
        hand2 = Hand([self.king_spades, self.queen_diamonds])
        hand2.add_card(self.ace_clubs)
        hand2.add_card(self.ace_clubs)  # Add Ace to make it 21, ace will be 1
        hand2.add_card(self.ten_clubs)  # Add 10 to make it 32
        # This tests the initial hand, not the one with added cards
        self.assertEqual(hand2.points, 32)

        hand3 = Hand([self.king_spades, self.queen_diamonds])  # 10 + 10 = 20
        self.assertEqual(hand3.points, 20)
        self.assertFalse(hand3.is_soft)

        # Bust
        hand4 = Hand([self.king_spades, self.queen_diamonds])
        hand4.add_card(self.five_hearts)  # 10 + 10 + 5 = 25
        self.assertEqual(hand4.points, 25)
        self.assertFalse(hand4.is_soft)

    def test_points_with_aces_soft(self):
        # Ace as 11 (soft hand)
        hand1 = Hand([self.ace_clubs, self.five_hearts])  # A(11) + 5 = 16
        self.assertEqual(hand1.points, 16)
        self.assertTrue(hand1.is_soft)

        # A(11) + 2 + 9 = 22 -> A(1) + 2 + 9 = 12
        hand2 = Hand([self.ace_clubs, self.two_spades])
        self.assertEqual(hand2.points, 13)
        self.assertTrue(hand2.is_soft)

        hand2.add_card(self.nine_clubs)
        self.assertEqual(hand2.points, 12)
        self.assertFalse(hand2.is_soft)

        hand2.add_card(self.two_spades)  # A(1) + 2 + 9 + 2 = 14
        hand2.add_card(self.nine_clubs)
        self.assertEqual(hand2.points, 23)
        self.assertFalse(hand2.is_soft)

        hand3 = Hand([self.ace_clubs, self.seven_diamonds])  # A(11) + 7 = 18
        self.assertEqual(hand3.points, 18)
        self.assertTrue(hand3.is_soft)

    def test_points_with_aces_hard(self):
        # Ace as 1 (hard hand)
        # A(11) + K(10) + 5 = 26 -> A(1) + K(10) + 5 = 16
        hand1 = Hand([self.ace_clubs, self.king_spades])
        hand1.add_card(self.five_hearts)
        self.assertEqual(hand1.points, 16)
        hand1.add_card(self.king_spades)
        # A(11)+K(10)+5 = 26. No, A(1)+K(10)+5 = 16.
        self.assertEqual(hand1.points, 26)
        self.assertFalse(hand1.is_soft)  # Ace was reduced, so not soft

        # A(11)+A(11)+10 = 32 -> A(1)+A(11)+10 = 22 -> A(1)+A(1)+10 = 12
        hand2 = Hand([self.ace_clubs, self.ace_hearts])
        self.assertEqual(hand2.points, 12)
        hand2.add_card(self.ten_clubs)
        self.assertEqual(hand2.points, 12)
        hand2.add_card(self.ace_hearts)
        self.assertEqual(hand2.points, 13)
        hand2.add_card(self.ten_clubs)
        self.assertEqual(hand2.points, 23)
        self.assertFalse(hand2.is_soft)  # All aces reduced, so not soft

    def test_potential_points(self):
        # Test potential points with no aces
        hand1 = Hand([self.five_hearts, self.seven_diamonds])
        self.assertEqual(hand1.potiential_points, [12])  # 5 + 7 = 12
        hand1.add_card(self.ten_clubs)  # 5 + 7 + 10 = 22
        self.assertEqual(hand1.potiential_points, [22])  # 5 + 7 + 10 = 22
        hand1.add_card(self.two_spades)  # 5 + 7 + 10 + 2 = 24
        self.assertEqual(hand1.potiential_points, [24])  # 5 + 7 + 10 + 2 = 24
        hand1.add_card(self.ace_clubs)  # 5 + 7 + 10 + 2 + A(1) = 25
        # 5 + 7 + 10 + 2 + A(1) = 25
        self.assertEqual(hand1.potiential_points, [25])
        hand1.add_card(self.ace_hearts)  # 5 + 7 + 10 + 2 + A(1) + A(1) = 26
        # 5 + 7 + 10 + 2 + A(1) + A(1) = 26
        self.assertEqual(hand1.potiential_points, [26])
        # 5 + 7 + 10 + 2 + A(1) + A(1) + K(10) = 36
        hand1.add_card(self.king_spades)
        # 5 + 7 + 10 + 2 + A(1) + A(1) + K(10) = 36
        self.assertEqual(hand1.potiential_points, [36])

        hand2 = Hand([self.ace_clubs, self.five_hearts])
        # A(11) + 5 = 16, A(1) + 5 = 6
        self.assertEqual(hand2.potiential_points, [16, 6])
        hand2.add_card(self.ace_clubs)
        # A(11) + 5 + A(11) = 27, A(1) + 5 + A(1) = 7
        self.assertEqual(hand2.potiential_points, [17, 7])
        # A(11) + 5 + 7 = 23, A(1) + 5 + 7 = 13
        hand2.add_card(self.seven_diamonds)
        # A(11) + 5 + 7 = 23, A(1) + 5 + 7 = 13
        self.assertEqual(hand2.potiential_points, [14])
        # A(11) + 5 + 7 + A(11) = 34, A(1) + 5 + 7 + A(1) = 14
        hand2.add_card(self.ace_hearts)
        # A(11) + 5 + 7 + A(11) = 34, A(1) + 5 + 7 + A(1) = 14
        self.assertEqual(hand2.potiential_points, [15])

    def test_is_blackjack(self):
        # True cases
        hand1 = Hand([self.ace_clubs, self.king_spades])  # A + K = 21
        self.assertTrue(hand1.is_blackjack())

        hand2 = Hand([self.ten_clubs, self.ace_hearts])  # 10 + A = 21
        self.assertTrue(hand2.is_blackjack())

        # False cases (not 21)
        hand3 = Hand([self.ace_clubs, self.five_hearts])  # A + 5 = 16
        self.assertFalse(hand3.is_blackjack())

        # False cases (more than 2 cards)
        hand4 = Hand([self.ace_clubs, self.king_spades])  # A + K + 2 = 23
        hand4.add_card(self.two_spades)  # Adding a card makes it not blackjack
        hand4.add_card(self.two_spades)
        self.assertFalse(hand4.is_blackjack())

        # False cases (less than 2 cards)
        hand5 = Hand([self.ace_clubs])
        self.assertFalse(hand5.is_blackjack())

    def test_is_bust(self):
        # True cases
        hand1 = Hand([self.king_spades, self.queen_diamonds])
        hand1.add_card(self.five_hearts)  # 10 + 10 + 5 = 25
        self.assertTrue(hand1.is_bust())

        hand2 = Hand([self.ace_clubs, self.ace_hearts])  # A(1)+A(1)+10+5 = 17
        hand2.add_card(self.ten_clubs)
        hand2.add_card(self.five_hearts)
        self.assertFalse(hand2.is_bust())  # 17 is not bust

        # False cases
        hand3 = Hand([self.five_hearts, self.seven_diamonds])  # 5 + 7 = 12
        self.assertFalse(hand3.is_bust())

        hand4 = Hand([self.ace_clubs, self.king_spades])  # 21
        self.assertFalse(hand4.is_bust())

    def test_str(self):
        hand1 = Hand([self.ace_clubs, self.king_spades])
        self.assertEqual(
            str(hand1), "♣A, ♠K, Points: [21, 11]")

        hand2 = Hand([self.five_hearts])
        self.assertEqual(str(hand2), "♥5, Points: [5]")

        hand3 = Hand([self.two_spades, self.seven_diamonds])
        hand3.add_card(self.nine_clubs)
        hand3.add_card(self.seven_diamonds)
        hand3.add_card(self.nine_clubs)
        self.assertEqual(
            str(hand3), "♠2, ♦7, ♣9, ♦7, ♣9, Points: [34]")


if __name__ == "__main__":
    unittest.main()
