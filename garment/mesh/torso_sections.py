"""Torso envelopes from horizontal triangle cuts, without an interior ray origin."""

import math


def convex_hull(points):
    points = sorted(set(points))
    if len(points) < 3:
        return []

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    lower, upper = [], []
    for chain, sequence in ((lower, points), (upper, reversed(points))):
        for point in sequence:
            while len(chain) >= 2 and cross(chain[-2], chain[-1], point) <= 0:
                chain.pop()
            chain.append(point)
    return lower[:-1] + upper[:-1]


def signed_area(hull):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(hull, hull[1:] + hull[:1])) / 2


class TorsoSections:
    """Select the central cut component and use its convex garment envelope.

    Convex envelopes intentionally span body concavities. They are not repaired
    body surfaces and do not imply simulated cloth or collision guarantees.
    """

    def __init__(self, vertices, triangles, height):
        self.vertices = vertices
        self.triangles = triangles
        self.tolerance = max(height * 1e-6, 1e-8)
        self.middle_x = (min(p[0] for p in vertices) + max(p[0] for p in vertices)) / 2
        self.cache = {}
        self.surface_cache = {}

    def surface_height(self, x, y, minimum, maximum):
        """Highest triangle intersection in a bounded shoulder height band."""
        band = (minimum, maximum)
        if band not in self.surface_cache:
            candidates = []
            for indices in self.triangles:
                a, b, c = (self.vertices[i] for i in indices)
                if max(a[2], b[2], c[2]) < minimum or min(a[2], b[2], c[2]) > maximum:
                    continue
                bx, by, cx, cy = b[0] - a[0], b[1] - a[1], c[0] - a[0], c[1] - a[1]
                determinant = bx * cy - by * cx
                if abs(determinant) > self.tolerance ** 2:
                    candidates.append((a, b, c, bx, by, cx, cy, determinant))
            self.surface_cache[band] = candidates
        highest = None
        for a, b, c, bx, by, cx, cy, determinant in self.surface_cache[band]:
            if not (min(a[0], b[0], c[0]) - self.tolerance <= x
                    <= max(a[0], b[0], c[0]) + self.tolerance
                    and min(a[1], b[1], c[1]) - self.tolerance <= y
                    <= max(a[1], b[1], c[1]) + self.tolerance):
                continue
            px, py = x - a[0], y - a[1]
            u = (px * cy - py * cx) / determinant
            v = (bx * py - by * px) / determinant
            if u >= -1e-9 and v >= -1e-9 and u + v <= 1 + 1e-9:
                z = a[2] + u * (b[2] - a[2]) + v * (c[2] - a[2])
                if minimum <= z <= maximum:
                    highest = z if highest is None else max(highest, z)
        return highest

    def section(self, z):
        if z in self.cache:
            return self.cache[z]
        graph, coordinates = {}, {}

        def key(point):
            return tuple(round(value / self.tolerance) for value in point)

        for triangle in self.triangles:
            points = [self.vertices[i] for i in triangle]
            if z < min(p[2] for p in points) or z > max(p[2] for p in points):
                continue
            hits = {}
            for a, b in zip(points, points[1:] + points[:1]):
                if a[2] == b[2]:
                    continue
                t = (z - a[2]) / (b[2] - a[2])
                if 0 <= t <= 1:
                    point = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                    hits[key(point)] = point
            if len(hits) != 2:
                continue
            first, second = hits
            coordinates.update(hits)
            graph.setdefault(first, set()).add(second)
            graph.setdefault(second, set()).add(first)

        remaining, hulls = set(graph), []
        while remaining:
            pending, component = [next(iter(remaining))], set()
            while pending:
                current = pending.pop()
                if current not in component:
                    component.add(current)
                    pending.extend(graph[current] - component)
            remaining -= component
            hull = convex_hull([coordinates[k] for k in component])
            if len(hull) >= 3 and signed_area(hull) > self.tolerance ** 2:
                hulls.append(hull)
        central = [h for h in hulls
                   if min(p[0] for p in h) <= self.middle_x <= max(p[0] for p in h)]
        hull = max(central, key=signed_area) if central else []
        self.cache[z] = hull
        return hull

    def center(self, z):
        hull = self.section(z)
        if not hull:
            raise ValueError("No central torso section at requested height")
        area = signed_area(hull)
        x, y = 0.0, 0.0
        for a, b in zip(hull, hull[1:] + hull[:1]):
            cross = a[0] * b[1] - b[0] * a[1]
            x += (a[0] + b[0]) * cross
            y += (a[1] + b[1]) * cross
        return x / (6 * area), y / (6 * area)

    def radius(self, z, angle):
        hull = self.section(z)
        if not hull:
            return None
        cx, cy = self.center(z)
        dx, dy = math.cos(angle), math.sin(angle)
        distances = []
        for a, b in zip(hull, hull[1:] + hull[:1]):
            ex, ey = b[0] - a[0], b[1] - a[1]
            denominator = dx * ey - dy * ex
            if abs(denominator) < 1e-12:
                continue
            ax, ay = a[0] - cx, a[1] - cy
            distance = (ax * ey - ay * ex) / denominator
            along = (ax * dy - ay * dx) / denominator
            if distance > 0 and -1e-9 <= along <= 1 + 1e-9:
                distances.append(distance)
        return min(distances) if distances else None
