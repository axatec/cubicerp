# -*- coding: utf-8 -*-
from datetime import datetime
from mock import patch

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
class TestTheoreticalAmount(TransactionCase):
    def setUp(self):
        super(TestTheoreticalAmount, self).setUp()
        cr, uid, = self.cr, self.uid
        budget_budget_id = self.registry('budget.budget').create(cr, uid, {
            'name': 'test budget name',
            'code': 'test budget code',
            'date_from': '2014-01-01',
            'date_to': '2014-12-31',
        })
        budget_budget_lines_obj = self.registry('budget.budget.lines')
        budget_budget_lines_id = budget_budget_lines_obj.create(cr, uid, {
            'budget_budget_id': budget_budget_id,
            'budget_position_id': self.ref('account_budget.account_budget_post_sales0'),
            'date_from': '2014-01-01',
            'date_to': '2014-12-31',
            'planned_amount': -364,
        })
        self.line = budget_budget_lines_obj.browse(cr, uid, budget_budget_lines_id)

        self.patcher = patch('openerp.addons.account_budget.account_budget.datetime', wraps=datetime)
        self.mock_datetime = self.patcher.start()

    def assertFloatEqual(self, value1, value2, *args, **kwargs):
        """ Compare two values of the field theoritical_amount """
        digits = type(self.line).theoritical_amount.digits
        result = float_compare(value1, value2, precision_digits=digits[1])
        return self.assertFalse(result, *args, **kwargs)

    def test_01(self):
        """Start"""
        date = datetime.strptime('2014-01-01 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, 0)

    def test_02(self):
        """After 24 hours"""
        date = datetime.strptime('2014-01-02 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -1)

    def test_03(self):
        """After 36 hours"""
        date = datetime.strptime('2014-01-02 12:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -1.5)

    def test_04(self):
        """After 48 hours"""
        date = datetime.strptime('2014-01-03 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -2)

    def test_05(self):
        """After 10 days"""
        date = datetime.strptime('2014-01-11 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -10)

    def test_06(self):
        """After 50 days"""
        date = datetime.strptime('2014-02-20 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -50)

    def test_07(self):
        """After 182 days, exactly half of the budget line"""
        date = datetime.strptime('2014-07-02 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -182)

    def test_08(self):
        """After 308 days at noon"""
        date = datetime.strptime('2014-11-05 12:00:00', DEFAULT_SERVER_DATETIME_FORMAT)  # remember, remember
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -308.5)

    def test_09(self):
        """One day before"""
        date = datetime.strptime('2014-12-30 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -363)

    def test_10(self):
        """At last"""
        date = datetime.strptime('2014-12-31 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        self.mock_datetime.now.return_value = date
        self.assertFloatEqual(self.line.theoritical_amount, -364)

    def tearDown(self):
        self.patcher.stop()
        super(TestTheoreticalAmount, self).tearDown()
