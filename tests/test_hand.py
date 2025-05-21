import unittest
from models.card import Card, Suit, Rank
from models.hand import Hand

class TestHand(unittest.TestCase):

    def test_blackjack(self):
        hand = Hand([Card(Suit.Clubs,Rank.ACE), Card(Suit.Clubs,Rank.KING)])
        hand.get_points()
        self.assertEqual(hand.final_points, 21)
        self.assertTrue(hand.is_blackjack())
        self.assertFalse(hand.is_bust())

    def test_bust(self):
        hand = Hand([Card(Suit.Clubs,Rank.KING), Card(Suit.Clubs,Rank.KING)])
        hand.add_card(Card(Suit.Clubs,Rank.FIVE))
        hand.get_points()
        self.assertTrue(hand.is_bust())
        self.assertFalse(hand.is_blackjack())

    def test_soft_ace_hand(self):
        hand = Hand([Card(Suit.Clubs,Rank.ACE), Card(Suit.Clubs,Rank.FIVE)])
        hand.add_card(Card(Suit.Clubs,Rank.FIVE))
        hand.get_points()
        self.assertEqual(hand.final_points, 21)
        self.assertTrue(hand.is_blackjack() or not hand.is_bust())

    def test_multi_aces(self):
        hand = Hand([Card(Suit.Clubs,Rank.ACE), Card(Suit.Clubs,Rank.ACE)])
        hand.add_card(Card(Suit.Clubs,Rank.NINE))
        hand.get_points()
        self.assertEqual(hand.final_points, 21)

    def test_invalid_init(self):
        with self.assertRaises(ValueError):
            Hand([Card(Suit.Clubs,Rank.TWO), Card(Suit.Clubs,Rank.THREE), Card(Suit.Clubs,Rank.FOUR)])

    def test_split_invalid_pair(self):
        hand = Hand([Card(Suit.Clubs,Rank.THREE), Card(Suit.Clubs,Rank.FOUR)])
        with self.assertRaises(ValueError):
            # simulate calling the commented-out split
            hand.split([Card(Suit.Clubs,Rank.THREE), Card(Suit.Clubs,Rank.FOUR)])

if __name__ == '__main__':
    unittest.main()
