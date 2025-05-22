import unittest
from models.card import Card, Suit, Rank
from models.hand import Hand

class TestHand(unittest.TestCase):

    def test_blackjack(self):
        hand = Hand([Card(Suit.Clubs,Rank.ACE), Card(Suit.Clubs,Rank.KING)])
        self.assertEqual(hand.points, 21)
        self.assertTrue(hand.is_blackjack())
        self.assertFalse(hand.is_bust())

        hand = Hand([Card(Suit.Clubs, Rank.TWO), Card(Suit.Clubs, Rank.KING)])
        hand.add_card(Card(Suit.Spades, Rank.NINE))
        self.assertEqual(hand.points, 21)
        self.assertFalse(hand.is_blackjack())
        self.assertFalse(hand.is_bust())

    def test_bust(self):
        hand = Hand([Card(Suit.Clubs,Rank.KING), Card(Suit.Clubs,Rank.KING)])
        hand.add_card(Card(Suit.Clubs, Rank.FIVE))
        self.assertTrue(hand.is_bust())
        self.assertFalse(hand.is_blackjack())

    def test_soft_ace_hand(self):
        hand = Hand([Card(Suit.Clubs,Rank.ACE), Card(Suit.Clubs,Rank.FIVE)])
        hand.add_card(Card(Suit.Clubs, Rank.FIVE))
        self.assertEqual(hand.points, 21)
        self.assertTrue(hand.is_blackjack() or not hand.is_bust())

    def test_multi_aces(self):
        hand = Hand([Card(Suit.Clubs,Rank.ACE), Card(Suit.Clubs,Rank.ACE)])
        hand.add_card(Card(Suit.Clubs,Rank.NINE))
        self.assertEqual(hand.points, 21)

    # def test_multi_aces_potential(self):
    #     hand = Hand([Card(Suit.Clubs, Rank.ACE), Card(Suit.Clubs, Rank.KING)])
    #     self.assertEqual(hand.get_points(), [11, 21])
    #     hand.add_card(Card(Suit.Clubs, Rank.NINE))
    #     self.assertEqual(hand.get_points(), [20])

    def test_invalid_init(self):
        with self.assertRaises(ValueError):
            Hand([Card(Suit.Clubs,Rank.TWO), Card(Suit.Clubs,Rank.THREE), Card(Suit.Clubs,Rank.FOUR)])

    def test_split_invalid_pair(self):
        hand = Hand([Card(Suit.Clubs,Rank.THREE), Card(Suit.Clubs,Rank.FOUR)])
        with self.assertRaises(ValueError):
            # simulate calling the commented-out split
            hand.split()

if __name__ == '__main__':
    unittest.main()
