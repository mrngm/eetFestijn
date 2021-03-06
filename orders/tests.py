# coding=utf-8
from django.test import TestCase
from orders.models import Item, Order, ItemOrder, Discount
from django.utils import timezone


class ItemTestCase(TestCase):
    def test_real_price(self):
        knakworst = Item.objects.get(name="Knakworst")
        friet = Item.objects.get(name="Friet oorlog (klein)")
        aardappel = Item.objects.get(name="extra ras/aardappel")
        self.assertEqual(knakworst.real_price(), 210)
        self.assertEqual(friet.real_price(), 240)
        self.assertEqual(aardappel.real_price(), 25)

    def test_name(self):
        knakworst = Item.objects.get(name="Knakworst")
        self.assertEqual(str(knakworst), "Knakworst")


class OrderTestCase(TestCase):
    def setUp(self):
        Order.objects.create(name="Test Order 1")
        Order.objects.create(name="Test Order 2")
        knakworst = Item.objects.get(name="Knakworst")
        friet = Item.objects.get(name="Friet oorlog (klein)")
        aardappel = Item.objects.get(name="extra ras/aardappel")
        self.items = [knakworst, friet, aardappel]

    def test_duplicates(self):
        order = Order.objects.get(name="Test Order 1")
        ItemOrder.objects.create(item=self.items[0], order=order)
        ItemOrder.objects.create(item=self.items[0], order=order)
        order.save()
        self.assertEqual(order.total(), 420)
        self.assertEqual(len(order.items.all()), 2)

    def test_total(self):
        order = Order.objects.get(name="Test Order 1")
        for item in self.items:
            ItemOrder.objects.create(item=item, order=order)
        order.save()
        self.assertEqual(order.total(), 475)

    def test_grandtotal(self):
        order1 = Order.objects.get(name="Test Order 1")
        order2 = Order.objects.get(name="Test Order 2")
        for item in self.items:
            ItemOrder.objects.create(item=item, order=order1)
            ItemOrder.objects.create(item=item, order=order2)
        order1.save()
        order2.save()
        self.assertEqual(Order.grandtotal(), 950)

    def test_name(self):
        self.assertIn("Test Order 1",
                      str(Order.objects.get(name="Test Order 1")))

    def test_itemstring(self):
        order1 = Order.objects.get(name="Test Order 1")
        for item in self.items:
            ItemOrder.objects.create(item=item, order=order1)
        self.assertIn("Knakworst", order1.itemstring())
        self.assertIn("extra ras/aardappel", order1.itemstring())


class ItemOrderTestCase(TestCase):
    def setUp(self):
        self.order1 = Order.objects.create(name="Test Order 1")
        self.order2 = Order.objects.create(name="Test Order 2")
        self.knakworst = Item.objects.get(name="Knakworst")
        self.friet = Item.objects.get(name="Friet oorlog (klein)")

    def test_str(self):
        for order in (self.order1, self.order2):
            for item in (self.knakworst, self.friet):
                io = ItemOrder.objects.create(item=item, order=order)
                self.assertEqual(str(item), str(io))


class DiscountTestCase(TestCase):
    def setUp(self):
        self.testdiscount1 = Discount.objects.create(
            name="Test Discount 1", relative=True, value=200,
            days=str(timezone.now().weekday()))
        self.testdiscount2 = Discount.objects.create(
            name="Test Discount 2", relative=False, value=600,
            days=str(timezone.now().weekday()))

    def test_relative_discount(self):
        item = Item.objects.create(name="Testitem", price=800)
        item.discounts.add(self.testdiscount1)
        self.assertEqual(item.real_price(), 600)

    def test_absolute_discount(self):
        item = Item.objects.create(name="Testitem", price=700)
        item.discounts.add(self.testdiscount2)
        self.assertEqual(item.real_price(), 600)

    def test_absolute_cheaper(self):
        item = Item.objects.create(name="Testitem", price=500)
        item.discounts.add(self.testdiscount2)
        self.assertEqual(item.real_price(), 500)

    def test_active(self):
        self.assertTrue(self.testdiscount1.is_active())

    def test_inactive(self):
        testdiscount = Discount.objects.create(
            name="Testdiscount", relative=False, value=600,
            days='')
        self.assertFalse(testdiscount.is_active())

    def test_item_discount_name(self):
        item = Item.objects.create(name="Testitem", price=800)
        item.discounts.add(self.testdiscount1)
        self.assertEqual(item.discountstring(), "Test Discount 1")

    def test_item_multiple_discount_names(self):
        item = Item.objects.create(name="Testitem", price=1000)
        item.discounts.add(self.testdiscount1)
        item.discounts.add(self.testdiscount2)
        self.assertIn(item.discountstring(),
                      ["Test Discount 1, Test Discount 2",
                       "Test Discount 2, Test Discount 1"])


class FestPopulateTestCase(TestCase):
    def test_totalnumber(self):
        self.assertEqual(190-2+1+19, Item.objects.count())
        self.assertEqual(3, Discount.objects.count())
