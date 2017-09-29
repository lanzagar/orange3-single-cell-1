import pickle
import unittest

import numpy as np

from Orange.data import Table

from orangecontrib.single_cell.preprocess.scnormalize import SCNormalizer


class ScNormalizeTest(unittest.TestCase):

    def setUp(self):
        self.iris = Table("iris")

    def test_normalize_no_group(self):
        # Fit with projector
        pp = SCNormalizer(log_base=None)
        data = pp(self.iris)

        row_sums = data.X.sum(axis=1)
        np.testing.assert_almost_equal(row_sums, row_sums[0])

    def test_normalize_with_group(self):
        pp = SCNormalizer(equalize_var=self.iris.domain.class_var,
                          log_base=None)
        data = pp(self.iris)

        group1, group2, group3 = [self.iris.Y == i for i in range(3)]
        med1 = np.median(data.X[group1].sum(axis=1))
        med2 = np.median(data.X[group2].sum(axis=1))
        med3 = np.median(data.X[group3].sum(axis=1))
        # Group medians should be equal
        self.assertAlmostEqual(med1, med2)
        self.assertAlmostEqual(med2, med3)

    def test_normalize_log(self):
        LOG_BASE = 2.7

        pp = SCNormalizer(normalize_cells=False, log_base=LOG_BASE)
        data = pp(self.iris)

        expected_X = np.log(1 + self.iris.X) / np.log(LOG_BASE)
        np.testing.assert_almost_equal(data.X, expected_X)

    def test_normalize_works_as_preprocessor(self):
        pp = SCNormalizer(normalize_cells=False, log_base=2)
        data = pp(self.iris)

        data2 = self.iris.transform(data.domain)

        np.testing.assert_almost_equal(data.X, data2.X)
        np.testing.assert_array_equal(data.ids, data2.ids)

    def test_normalized_data_can_be_pickled(self):
        pp = SCNormalizer(normalize_cells=False, log_base=2)
        data = pp(self.iris)

        data2 = pickle.loads(pickle.dumps(data))
        np.testing.assert_almost_equal(data.X, data2.X)
        np.testing.assert_array_equal(data.ids, data2.ids)

        data3 = self.iris.transform(data2.domain)
        np.testing.assert_almost_equal(data.X, data3.X)
        np.testing.assert_array_equal(data.ids, data3.ids)
