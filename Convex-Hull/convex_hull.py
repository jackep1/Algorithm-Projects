import math
import sys
from typing import List
from typing import Tuple

EPSILON = sys.float_info.epsilon
Point = Tuple[int, int]


def y_intercept(p1: Point, p2: Point, x: int) -> float:
    """
    Given two points, p1 and p2, an x coordinate from a vertical line,
    compute and return the y-intercept of the line segment p1->p2
    with the vertical line passing through x.
    """
    x1, y1 = p1
    x2, y2 = p2
    slope = (y2 - y1) / (x2 - x1)
    return y1 + (x - x1) * slope


def triangle_area(a: Point, b: Point, c: Point) -> float:
    """
    Given three points a,b,c,
    computes and returns the area defined by the triangle a,b,c.
    Note that this area will be negative if a,b,c represents a clockwise sequence,
    positive if it is counter-clockwise,
    and zero if the points are collinear.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    return ((cx - bx) * (by - ay) - (bx - ax) * (cy - by)) / 2


def is_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) < -EPSILON


def is_counter_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a counter-clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) > EPSILON


def collinear(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c are collinear
    (subject to floating-point precision)
    """
    return abs(triangle_area(a, b, c)) <= EPSILON


def sort_clockwise(points: List[Point]):
    """
    Sorts `points` by ascending clockwise angle from +x about the centroid,
    breaking ties first by ascending x value and then by ascending y value.

    The order of equal points is not modified

    Note: This function modifies its argument
    """
    # Trivial cases don't need sorting, and this dodges divide-by-zero errors
    if len(points) < 2:
        return

    # Compute the centroid
    centroid_x = sum(p[0] for p in points) / len(points)
    centroid_y = sum(p[1] for p in points) / len(points)

    # Sort by ascending clockwise angle from +x, breaking ties with ^x then ^y
    def sort_key(point: Point):
        angle = math.atan2(point[1] - centroid_y, point[0] - centroid_x)
        normalized_angle = (angle + math.tau) % math.tau
        return normalized_angle, point[0], point[1]

    # Sort the points
    points.sort(key=sort_key)


def base_case_hull(points: List[Point]) -> List[Point]:
    """
    Base case of the recursive algorithm.
    """
    # TODO: You need to implement this function.
    num_points = len(points)

    # Case of zero points: no hull
    if num_points == 0:
        return []
    # Case of one point: hull is the point
    if num_points == 1:
        return points
    # Case of two points: hull is the two points
    if num_points == 2:
        return points
    if num_points == 3:
        sort_clockwise(points)
        points.reverse()
        return points
    raise ValueError("The base_case_hull() function shouldn't be called with more than three points!")


def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull.
    """
    # TODO: Implement a correct computation of the convex hull
    #  using the divide-and-conquer algorithm
    # TODO: Document your Initialization, Maintenance and Termination invariants.
    num_points = len(points)

    # If three or fewer points, base case applies
    if num_points <= 3:
        return base_case_hull(points)

    # Sort by x-coordinate (y-coordinate breaks ties)
    points.sort(key=lambda p: (p[0], p[1]))

    # Divide points to sub-problem
    mid = num_points // 2
    left_hull = compute_hull(points[:mid])
    right_hull = compute_hull(points[mid:])

    # Merge the two hulls
    return merge_hulls(left_hull, right_hull)


def merge_hulls(left: List[Point], right: List[Point]) -> List[Point]:
    """
    Merge two convex hulls into a single convex hull.
    """
    # If one of the hulls is empty, return the other
    if not left:
        return right
    if not right:
        return left

    combined = left + right
    if len(combined) >= 3 and all(collinear(combined[0], combined[1], p) for p in combined[2:]):
        return [min(combined), max(combined)]    

    # Find the rightmost point of the left hull and the leftmost point of the right hull
    leftmost_right = min(right, key=lambda p: p[0])
    rightmost_left = max(left, key=lambda p: p[0])

    left_index = left.index(rightmost_left)
    right_index = right.index(leftmost_right)

    # Finding upper tangent
    while True:
        updated = False

        # Move right point up as long as the tangent is not correct
        while is_counter_clockwise(left[left_index], right[right_index], right[(right_index - 1) % len(right)]):
            right_index = (right_index - 1) % len(right)
            updated = True

        # Move left point up as long as the tangent is not correct
        while is_counter_clockwise(left[left_index], right[right_index], left[(left_index + 1) % len(left)]):
            left_index = (left_index + 1) % len(left)
            updated = True

        if not updated:
            break

    upper_tangent_left = left_index
    upper_tangent_right = right_index

    # Reset indices to find lower tangent
    left_index = left.index(rightmost_left)
    right_index = right.index(leftmost_right)

    # Finding lower tangent
    while True:
        updated = False

        # Move right point down as long as the tangent is not correct
        while is_clockwise(left[left_index], right[right_index], right[(right_index + 1) % len(right)]):
            right_index = (right_index + 1) % len(right)
            updated = True

        # Move left point down as long as the tangent is not correct
        while is_clockwise(left[left_index], right[right_index], left[(left_index - 1) % len(left)]):
            left_index = (left_index - 1) % len(left)
            updated = True

        if not updated:
            break

    lower_tangent_left = left_index
    lower_tangent_right = right_index

    # Construct the merged hull by traversing the left and right hulls from upper to lower tangents
    hull = []

    # Add points from the left hull, between the upper and lower tangent
    i = upper_tangent_left
    while i != lower_tangent_left:
        hull.append(left[i])
        i = (i + 1) % len(left)
    hull.append(left[lower_tangent_left])

    # Add points from the right hull, between the lower and upper tangent
    i = lower_tangent_right
    while i != upper_tangent_right:
        hull.append(right[i])
        i = (i + 1) % len(right)
    hull.append(right[upper_tangent_right])

    return hull
