"""
Unit tests for landmarks space.
"""

import geomstats.backend as gs
import geomstats.tests
import tests.helper as helper

from geomstats.geometry.hypersphere import Hypersphere
from geomstats.geometry.landmarks_space import LandmarksSpace


class TestLandmarksSpaceMethods(geomstats.tests.TestCase):
    def setUp(self):
        s2 = Hypersphere(dimension=2)
        r3 = s2.embedding_manifold

        initial_point = [0., 0., 1.]
        initial_tangent_vec_a = [1., 0., 0.]
        initial_tangent_vec_b = [0., 1., 0.]
        initial_tangent_vec_c = [-1., 0., 0.]

        landmarks_a = s2.metric.geodesic(initial_point=initial_point,
                                     initial_tangent_vec=initial_tangent_vec_a)
        landmarks_b = s2.metric.geodesic(initial_point=initial_point,
                                     initial_tangent_vec=initial_tangent_vec_b)
        landmarks_c = s2.metric.geodesic(initial_point=initial_point,
                                     initial_tangent_vec=initial_tangent_vec_c)

        self.n_sampling_points = 10
        sampling_times = gs.linspace(0., 1., self.n_sampling_points)
        landmark_set_a = landmarks_a(sampling_times)
        landmark_set_b = landmarks_b(sampling_times)
        landmark_set_c = landmarks_c(sampling_times)

        self.n_landmark_sets = 5
        self.times = gs.linspace(0., 1., self.n_landmark_sets)
        self.atol = 1e-6
        gs.random.seed(1234)
        self.space_landmarks_in_euclidean_3d = LandmarksSpace(
                ambient_manifold=r3)
        self.space_landmarks_in_sphere_2d = LandmarksSpace(
                ambient_manifold=s2)
        self.l2_metric_s2 = self.space_landmarks_in_sphere_2d.l2_metric
        self.l2_metric_r3 = self.space_landmarks_in_euclidean_3d.l2_metric
        self.landmarks_a = landmark_set_a
        self.landmarks_b = landmark_set_b
        self.landmarks_c = landmark_set_c

    def test_belongs(self):
        result = self.space_landmarks_in_sphere_2d.belongs(self.landmarks_a)
        expected = gs.array([[True]])

        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_l2_metric_log_and_squared_norm_and_dist(self):
        """
        Test that squared norm of logarithm is squared dist.
        """
        tangent_vec = self.l2_metric_s2.log(
                landmarks=self.landmarks_b, base_landmarks=self.landmarks_a)
        log_ab = tangent_vec
        result = self.l2_metric_s2.squared_norm(
                vector=log_ab, base_point=self.landmarks_a)
        expected = self.l2_metric_s2.dist(self.landmarks_a, self.landmarks_b) ** 2
        expected = helper.to_scalar(expected)

        self.assertAllClose(result, expected)

    @geomstats.tests.np_and_tf_only
    def test_l2_metric_log_and_exp(self):
        """
        Test that exp and log are inverse maps.
        """
        tangent_vec = self.l2_metric_s2.log(
                landmarks=self.landmarks_b, base_landmarks=self.landmarks_a)
        result = self.l2_metric_s2.exp(tangent_vec=tangent_vec,
                                       base_landmarks=self.landmarks_a)
        expected = self.landmarks_b

        self.assertAllClose(result, expected, atol=self.atol)

    @geomstats.tests.np_and_tf_only
    def test_l2_metric_inner_product_vectorization(self):
        """
        Test the vectorization inner_product.
        """
        n_samples = self.n_landmark_sets
        landmarks_ab = self.l2_metric_s2.geodesic(
            self.landmarks_a, self.landmarks_b)
        landmarks_bc = self.l2_metric_s2.geodesic(
            self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        tangent_vecs = self.l2_metric_s2.log(
                landmarks=landmarks_bc, base_landmarks=landmarks_ab)

        result = self.l2_metric_s2.inner_product(
                tangent_vecs, tangent_vecs, landmarks_ab)

        self.assertAllClose(gs.shape(result), (n_samples, 1))

    @geomstats.tests.np_and_tf_only
    def test_l2_metric_dist_vectorization(self):
        """
        Test the vectorization of dist.
        """
        n_samples = self.n_landmark_sets
        landmarks_ab = self.l2_metric_s2.geodesic(
            self.landmarks_a, self.landmarks_b)
        landmarks_bc = self.l2_metric_s2.geodesic(
            self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        result = self.l2_metric_s2.dist(
                landmarks_ab, landmarks_bc)
        self.assertAllClose(gs.shape(result), (n_samples, 1))

    @geomstats.tests.np_and_tf_only
    def test_l2_metric_exp_vectorization(self):
        """
        Test the vectorization of exp.
        """
        landmarks_ab = self.l2_metric_s2.geodesic(
            self.landmarks_a, self.landmarks_b)
        landmarks_bc = self.l2_metric_s2.geodesic(
            self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        tangent_vecs = self.l2_metric_s2.log(
                landmarks=landmarks_bc, base_landmarks=landmarks_ab)

        result = self.l2_metric_s2.exp(
                tangent_vec=tangent_vecs,
                base_landmarks=landmarks_ab)
        self.assertAllClose(gs.shape(result), gs.shape(landmarks_ab))

    @geomstats.tests.np_and_tf_only
    def test_l2_metric_log_vectorization(self):
        """
        Test the vectorization of log.
        """
        landmarks_ab = self.l2_metric_s2.geodesic(
            self.landmarks_a, self.landmarks_b)
        landmarks_bc = self.l2_metric_s2.geodesic(
            self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        tangent_vecs = self.l2_metric_s2.log(
                landmarks=landmarks_bc, base_landmarks=landmarks_ab)

        result = tangent_vecs
        self.assertAllClose(gs.shape(result), gs.shape(landmarks_ab))

    @geomstats.tests.np_only
    def test_l2_metric_geodesic(self):
        """
        Test the geodesic method of L2Metric.
        """
        landmarks_ab = self.l2_metric_s2.geodesic(
            self.landmarks_a, self.landmarks_b)
        landmarks_bc = self.l2_metric_s2.geodesic(
            self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        result = landmarks_ab
        expected = gs.zeros(landmarks_ab.shape)
        for k in range(self.n_sampling_points):
            geod = self.l2_metric_s2.ambient_metric.geodesic(
                    initial_point=self.landmarks_a[k, :],
                    end_point=self.landmarks_b[k, :])
            expected[:, k, :] = geod(self.times)

        self.assertAllClose(result, expected)

        geod = self.l2_metric_s2.geodesic(
                initial_landmarks=landmarks_ab,
                end_landmarks=landmarks_bc)
