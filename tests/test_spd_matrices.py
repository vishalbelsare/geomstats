"""
Unit tests for the manifold of symmetric positive definite matrices.
"""

import warnings

import geomstats.backend as gs
import geomstats.tests
from geomstats.geometry.spd_matrices import (
    SPDMatrices,
    SPDMetricAffine,
    SPDMetricEuclidean,
    SPDMetricProcrustes
)


class TestSPDMatricesMethods(geomstats.tests.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)

        gs.random.seed(1234)

        self.n = 3
        self.space = SPDMatrices(n=self.n)
        self.metric_affine = SPDMetricAffine(n=self.n)
        self.metric_procrustes = SPDMetricProcrustes(n=self.n)
        self.metric_euclidean = SPDMetricEuclidean(n=self.n)
        self.metric_logeuclidean = SPDMetricLogEuclidean(n=self.n)
        self.n_samples = 4

    @geomstats.tests.np_and_tf_only
    def test_random_uniform_and_belongs(self):
        point = self.space.random_uniform()
        result = self.space.belongs(point)
        expected = gs.array([[True]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_random_uniform_and_belongs_vectorization(self):
        """
        Test that the random uniform method samples
        on the hypersphere space.
        """
        n_samples = self.n_samples
        points = self.space.random_uniform(n_samples=n_samples)
        result = self.space.belongs(points)
        self.assertAllClose(gs.shape(result), (n_samples, 1))

    @geomstats.tests.np_and_tf_only
    def vector_from_symmetric_matrix_and_symmetric_matrix_from_vector(self):
        sym_mat_1 = gs.array([[1., 0.6, -3.],
                              [0.6, 7., 0.],
                              [-3., 0., 8.]])
        vector_1 = self.space.vector_from_symmetric_matrix(sym_mat_1)
        result_1 = self.space.symmetric_matrix_from_vector(vector_1)
        expected_1 = sym_mat_1

        self.assertTrue(gs.allclose(result_1, expected_1))

        vector_2 = gs.array([1, 2, 3, 4, 5, 6])
        sym_mat_2 = self.space.symmetric_matrix_from_vector(vector_2)
        result_2 = self.space.vector_from_symmetric_matrix(sym_mat_2)
        expected_2 = vector_2

        self.assertTrue(gs.allclose(result_2, expected_2))

    @geomstats.tests.np_and_tf_only
    def vector_and_symmetric_matrix_vectorization(self):
        n_samples = self.n_samples
        vector = gs.random.rand(n_samples, 6)
        sym_mat = self.space.symmetric_matrix_from_vector(vector)
        result = self.space.vector_from_symmetric_matrix(sym_mat)
        expected = vector

        self.assertTrue(gs.allclose(result, expected))

        sym_mat = self.space.random_uniform(n_samples)
        vector = self.space.vector_from_symmetric_matrix(sym_mat)
        result = self.space.symmetric_matrix_from_vector(vector)
        expected = sym_mat

        self.assertTrue(gs.allclose(result, expected))

    @geomstats.tests.np_and_tf_only
    def test_differential_power(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 2.5, 1.5],
                               [0., 1.5, 2.5]])
        tangent_vec = gs.array([[2., 1., 1.],
                               [1., .5, .5],
                               [1., .5, .5]])
        power = .5
        result = self.space.differential_power(
            power=power,
            tangent_vec=tangent_vec,
            base_point=base_point)
        expected = gs.array([[[1., 1/3, 1/3],
                              [1/3, .125, .125],
                              [1/3, .125, .125]]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_inverse_differential_power(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 2.5, 1.5],
                               [0., 1.5, 2.5]])
        tangent_vec = gs.array([[1., 1 / 3, 1 / 3],
                                [1 / 3, .125, .125],
                                [1 / 3, .125, .125]])
        power = .5
        result = self.space.inverse_differential_power(
            power=power,
            tangent_vec=tangent_vec,
            base_point=base_point)
        expected = gs.array([[[2., 1., 1.],
                             [1., .5, .5],
                             [1., .5, .5]]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_differential_log(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 4.]])
        tangent_vec = gs.array([[1., 1., 3.],
                                [1., 1., 3.],
                                [3., 3., 4.]])
        result = self.space.differential_log(tangent_vec, base_point)
        x = 2*gs.log(2)
        expected = gs.array([[[1., 1., x],
                              [1., 1., x],
                              [x, x, 1]]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_inverse_differential_log(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 4.]])
        x = 2 * gs.log(2)
        tangent_vec = gs.array([[1., 1., x],
                                [1., 1., x],
                                [x, x, 1]])
        result = self.space.inverse_differential_log(tangent_vec, base_point)
        expected = gs.array([[[1., 1., 3.],
                              [1., 1., 3.],
                              [3., 3., 4.]]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_differential_exp(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., -1.]])
        tangent_vec = gs.array([[1., 1., 1.],
                                [1., 1., 1.],
                                [1., 1., 1.]])
        result = self.space.differential_exp(tangent_vec, base_point)
        x = gs.exp(1)
        y = gs.sinh(1)
        expected = gs.array([[[x, x, y],
                              [x, x, y],
                              [y, y, 1/x]]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_inverse_differential_exp(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., -1.]])
        x = gs.exp(1)
        y = gs.sinh(1)
        tangent_vec = gs.array([[x, x, y],
                                [x, x, y],
                                [y, y, 1/x]])
        result = self.space.inverse_differential_exp(tangent_vec, base_point)
        expected = gs.array([[[1., 1., 1.],
                              [1., 1., 1.],
                              [1., 1., 1.]]])
        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_procrustes_inner_product(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 1.5, .5],
                               [0., .5, 1.5]])
        tangent_vec_a = gs.array([[2., 1., 1.],
                                  [1., .5, .5],
                                  [1., .5, .5]])
        tangent_vec_b = gs.array([[1., 2., 4.],
                                  [2., 3., 8.],
                                  [4., 8., 5.]])
        metric = SPDMetricProcrustes(3)
        result = metric.inner_product(tangent_vec_a, tangent_vec_b, base_point)
        expected = 4

        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_power_affine_inner_product(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 2.5, 1.5],
                               [0., 1.5, 2.5]])
        tangent_vec = gs.array([[2., 1., 1.],
                               [1., .5, .5],
                               [1., .5, .5]])
        metric = SPDMetricAffine(3, power_affine=.5)
        result = metric.inner_product(tangent_vec, tangent_vec, base_point)
        expected = [[713/144]]

        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_power_euclidean_inner_product(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 2.5, 1.5],
                               [0., 1.5, 2.5]])
        tangent_vec = gs.array([[2., 1., 1.],
                                [1., .5, .5],
                                [1., .5, .5]])
        metric = SPDMetricEuclidean(3, power_euclidean=.5)
        result = metric.inner_product(tangent_vec, tangent_vec, base_point)
        expected = [[3472/576]]

        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_euclidean_exp_domain(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 2., 0.],
                               [0., 0., 3.]])
        tangent_vec = gs.array([[-1., 0., 0.],
                                [0., -.5, 0.],
                                [0., 0., 1.]])
        metric = self.metric_euclidean
        result = metric.exp_domain(tangent_vec, base_point)
        expected = gs.array([[-3, 1]])

        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_log_euclidean_inner_product(self):
        base_point = gs.array([[1., 0., 0.],
                               [0., 1., 0.],
                               [0., 0., 4.]])
        tangent_vec = gs.array([[1., 1., 3.],
                                [1., 1., 3.],
                                [3., 3., 4.]])
        metric = self.metric_logeuclidean
        result = metric.inner_product(tangent_vec, tangent_vec, base_point)
        x = 2 * gs.log(2)
        expected = 5.+4.*x**2

        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_log_and_exp_affine_invariant(self):
        base_point = gs.array([[5., 0., 0.],
                               [0., 7., 2.],
                               [0., 2., 8.]])
        point = gs.array([[9., 0., 0.],
                          [0., 5., 0.],
                          [0., 0., 1.]])

        metric = self.metric_affine
        log = metric.log(point=point, base_point=base_point)
        result = metric.exp(tangent_vec=log, base_point=base_point)
        expected = point

        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_log_and_exp_power_affine(self):
        base_point = gs.array([[5., 0., 0.],
                               [0., 7., 2.],
                               [0., 2., 8.]])
        point = gs.array([[9., 0., 0.],
                          [0., 5., 0.],
                          [0., 0., 1.]])
        metric = SPDMetricAffine(3, power_affine=.5)
        log = metric.log(point, base_point)
        result = metric.exp(log, base_point)
        expected = point
        self.assertAllClose(result, expected)

    def test_log_and_exp_logeuclidean(self):
        base_point = gs.array([[5., 0., 0.],
                               [0., 7., 2.],
                               [0., 2., 8.]])
        point = gs.array([[9., 0., 0.],
                          [0., 5., 0.],
                          [0., 0., 1.]])

        metric = self.metric_logeuclidean
        log = metric.log(point=point, base_point=base_point)
        result = metric.exp(tangent_vec=log, base_point=base_point)
        expected = point

        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_exp_and_belongs(self):
        n_samples = self.n_samples
        base_point = self.space.random_uniform(n_samples=1)
        tangent_vec = self.space.random_tangent_vec_uniform(
                                               n_samples=n_samples,
                                               base_point=base_point)
        metric = self.metric_affine
        exps = metric.exp(tangent_vec, base_point)
        result = self.space.belongs(exps)
        expected = gs.array([[True]] * n_samples)

        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_exp_vectorization(self):
        n_samples = self.n_samples
        one_base_point = self.space.random_uniform(n_samples=1)
        n_base_point = self.space.random_uniform(n_samples=n_samples)

        n_tangent_vec_same_base = self.space.random_tangent_vec_uniform(
                                                 n_samples=n_samples,
                                                 base_point=one_base_point)
        n_tangent_vec = self.space.random_tangent_vec_uniform(
                                                 n_samples=n_samples,
                                                 base_point=n_base_point)
        metric = self.metric_affine

        # Test with the 1 base_point, and several different tangent_vecs
        result = metric.exp(n_tangent_vec_same_base, one_base_point)

        self.assertAllClose(
            gs.shape(result), (n_samples, self.space.n, self.space.n))

        # Test with the same number of base_points and tangent_vecs
        result = metric.exp(n_tangent_vec, n_base_point)

        self.assertAllClose(
            gs.shape(result), (n_samples, self.space.n, self.space.n))

    @geomstats.tests.np_and_tf_only
    def test_log_vectorization(self):
        n_samples = self.n_samples
        one_base_point = self.space.random_uniform(n_samples=1)
        n_base_point = self.space.random_uniform(n_samples=n_samples)

        one_point = self.space.random_uniform(n_samples=1)
        n_point = self.space.random_uniform(n_samples=n_samples)
        metric = self.metric_affine

        # Test with different points, one base point
        result = metric.log(n_point, one_base_point)

        self.assertAllClose(
            gs.shape(result), (n_samples, self.space.n, self.space.n))

        # Test with the same number of points and base points
        result = metric.log(n_point, n_base_point)

        self.assertAllClose(
            gs.shape(result), (n_samples, self.space.n, self.space.n))

        # Test with the one point and n base points
        result = metric.log(one_point, n_base_point)

        self.assertAllClose(
            gs.shape(result), (n_samples, self.space.n, self.space.n))

    @geomstats.tests.np_and_tf_only
    def test_geodesic_and_belongs(self):
        initial_point = self.space.random_uniform()
        initial_tangent_vec = self.space.random_tangent_vec_uniform(
                                                n_samples=1,
                                                base_point=initial_point)
        metric = self.metric_affine
        geodesic = metric.geodesic(
                                   initial_point=initial_point,
                                   initial_tangent_vec=initial_tangent_vec)

        n_points = 10
        t = gs.linspace(start=0., stop=1., num=n_points)
        points = geodesic(t)
        result = self.space.belongs(points)
        expected = gs.array([[True]] * n_points)

        self.assertAllClose(result, expected)

    @geomstats.tests.np_only
    def test_squared_dist_is_symmetric(self):
        n_samples = self.n_samples

        point_1 = self.space.random_uniform(n_samples=1)
        point_2 = self.space.random_uniform(n_samples=1)

        metric = self.metric_affine
        sq_dist_1_2 = metric.squared_dist(point_1, point_2)
        sq_dist_2_1 = metric.squared_dist(point_2, point_1)

        self.assertAllClose(sq_dist_1_2, sq_dist_2_1)

        point_1 = self.space.random_uniform(n_samples=1)
        point_2 = self.space.random_uniform(n_samples=n_samples)

        sq_dist_1_2 = metric.squared_dist(point_1, point_2)
        sq_dist_2_1 = metric.squared_dist(point_2, point_1)

        self.assertAllClose(sq_dist_1_2, sq_dist_2_1)

        point_1 = self.space.random_uniform(n_samples=n_samples)
        point_2 = self.space.random_uniform(n_samples=1)

        sq_dist_1_2 = metric.squared_dist(point_1, point_2)
        sq_dist_2_1 = metric.squared_dist(point_2, point_1)

        self.assertAllClose(sq_dist_1_2, sq_dist_2_1)

        point_1 = self.space.random_uniform(n_samples=n_samples)
        point_2 = self.space.random_uniform(n_samples=n_samples)

        sq_dist_1_2 = metric.squared_dist(point_1, point_2)
        sq_dist_2_1 = metric.squared_dist(point_2, point_1)

        self.assertAllClose(sq_dist_1_2, sq_dist_2_1)

    @geomstats.tests.np_and_tf_only
    def test_squared_dist_vectorization(self):
        n_samples = self.n_samples
        point_1 = self.space.random_uniform(n_samples=n_samples)
        point_2 = self.space.random_uniform(n_samples=n_samples)

        metric = self.metric_affine
        result = metric.squared_dist(point_1, point_2)

        self.assertAllClose(gs.shape(result), (n_samples, 1))

        point_1 = self.space.random_uniform(n_samples=1)
        point_2 = self.space.random_uniform(n_samples=n_samples)

        result = metric.squared_dist(point_1, point_2)

        self.assertAllClose(gs.shape(result), (n_samples, 1))

        point_1 = self.space.random_uniform(n_samples=n_samples)
        point_2 = self.space.random_uniform(n_samples=1)

        result = metric.squared_dist(point_1, point_2)

        self.assertAllClose(gs.shape(result), (n_samples, 1))

        point_1 = self.space.random_uniform(n_samples=1)
        point_2 = self.space.random_uniform(n_samples=1)

        result = metric.squared_dist(point_1, point_2)

        self.assertAllClose(gs.shape(result), (1, 1))
