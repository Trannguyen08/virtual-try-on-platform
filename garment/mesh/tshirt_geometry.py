"""Synthetic open T-shirt surface; metres, Blender Z-up until GLB export.

This is a visual template, not a manufacturer size chart or cloth simulation.
The body sampler returns the distance to the torso surface along an XY ray.
"""

import math


EASE = {"XS": 0.012, "S": 0.018, "M": 0.025,
        "L": 0.035, "XL": 0.045, "XXL": 0.055}


def build_tshirt(height, floor, center, sample_radius, arm_directions, size="M",
                 sample_center=None, sample_shoulder_height=None):
    """Return vertices/quads, retaining four openings: neck, hem, two cuffs."""
    if not math.isfinite(height) or height <= 0:
        raise ValueError("T-shirt requires a finite positive body height")
    if size not in EASE:
        raise ValueError("Unsupported T-shirt size")
    vertices, faces, rows = [], [], []
    count = 32
    ease = EASE[size] * height / 1.7

    def lift_shoulder(point):
        if sample_shoulder_height is None:
            return point
        surface = sample_shoulder_height(point[0], point[1])
        if surface is None or not math.isfinite(surface):
            return point
        clearance = 0.006 * height / 1.7
        return point[0], point[1], max(point[2], surface + clearance)

    def ring(points):
        indices = list(range(len(vertices), len(vertices) + len(points)))
        vertices.extend(points)
        return indices

    def join(first, second, skip=()):
        for j in range(len(first)):
            if j not in skip:
                k = (j + 1) % len(first)
                faces.append((first[j], first[k], second[k], second[j]))

    # Closed torso rings up to the armpits. Ease changes circumference rather
    # than globally scaling the shirt away from the shoulders.
    levels = [0.46, 0.49, 0.53, 0.57, 0.61, 0.65, 0.69, 0.72]
    # A shirt hangs across the gap between the legs. Its hem cannot be fitted
    # by demanding a closed body cross-section below the pelvis. Extend the
    # lowest complete hip/waist profile downward instead of wrapping each leg.
    profiles = {
        level: [sample_radius(floor + level * height, 2 * math.pi * j / count)
                for j in range(count)]
        for level in levels[2:]
    }

    def valid(radius):
        return radius is not None and math.isfinite(radius) and radius > 0

    anchor = next((level for level in (0.53, 0.57, 0.61)
                   if all(valid(radius) for radius in profiles[level])), None)
    if anchor is None:
        raise ValueError("Cannot sample a continuous torso for T-shirt: "
                         "no complete hip/waist profile at height ratios 0.53-0.61")
    for level in levels:
        z = floor + level * height
        points = []
        profile = profiles[anchor] if level <= anchor else profiles[level]
        local_center = (sample_center(floor + max(level, anchor) * height)
                        if sample_center else center)
        for j in range(count):
            angle = 2 * math.pi * j / count
            radius = profile[j]
            if not valid(radius):
                raise ValueError("Cannot sample a continuous torso for T-shirt: "
                                 f"height ratio={level:.2f}, angular sample={j}/{count}")
            radius += ease
            points.append((local_center[0] + radius * math.cos(angle),
                           local_center[1] + radius * math.sin(angle), z))
        rows.append(ring(points))
        if len(rows) > 1:
            join(rows[-2], rows[-1])

    underarm = rows[-1]
    upper = [underarm]
    # Each lateral gap is later sewn to a sleeve, sharing boundary vertices.
    gaps = tuple(range(0, 4)) + tuple(range(12, 20)) + tuple(range(28, 32))
    for step in range(1, 5):
        t = step / 4
        points = []
        for j in range(count):
            angle = 2 * math.pi * j / count
            start = vertices[underarm[j]]
            shoulder = (center[0] + (0.145 * height + ease) * math.cos(angle),
                        center[1] + (0.075 * height + ease) * math.sin(angle),
                        floor + height * (0.815 - 0.018 * abs(math.cos(angle))))
            point = tuple(a + (b - a) * t for a, b in zip(start, shoulder))
            # Keep the upper chest/back outside the sampled torso as well.
            # The lateral openings are intentionally handled by the sleeves.
            if 4 <= j <= 12 or 20 <= j <= 28:
                radius = sample_radius(point[2], angle)
                if radius is not None and math.isfinite(radius) and radius > 0:
                    local_center = sample_center(point[2]) if sample_center else center
                    proposed = math.hypot(point[0] - local_center[0], point[1] - local_center[1])
                    radius = max(proposed, radius + ease)
                    point = (local_center[0] + radius * math.cos(angle),
                             local_center[1] + radius * math.sin(angle), point[2])
            points.append(lift_shoulder(point) if step == 4 else point)
        upper.append(ring(points))
        join(upper[-2], upper[-1], gaps)

    # Shoulder panels converge to an actual neckline, with a deeper front.
    previous = upper[-1]
    for step in range(1, 5):
        t = step / 4
        points = []
        for j in range(count):
            angle = 2 * math.pi * j / count
            start = vertices[upper[-1][j]]
            neck = (center[0] + 0.058 * height * math.cos(angle),
                    center[1] + 0.048 * height * math.sin(angle),
                    floor + height * (0.85 - 0.025 * max(0, -math.sin(angle))))
            point = tuple(a + (b - a) * t for a, b in zip(start, neck))
            # Lift the shoulder bridge over the body, retaining the neckline.
            points.append(lift_shoulder(point) if step < 4 else point)
        current = ring(points)
        join(previous, current)
        previous = current

    for side, start_angle in ((1, 28), (-1, 12)):
        angles = [(start_angle + j) % count for j in range(9)]
        boundary = [upper[0][j] for j in angles]
        boundary += [upper[r][angles[-1]] for r in range(1, 5)]
        boundary += [upper[4][j] for j in reversed(angles[:-1])]
        boundary += [upper[r][angles[0]] for r in range(3, 0, -1)]
        origin = tuple(sum(vertices[i][axis] for i in boundary) / len(boundary)
                       for axis in range(3))
        dx, dz = arm_directions[side]
        length = math.hypot(dx, dz)
        if not math.isfinite(length) or length <= 0 or dx * side <= 0:
            raise ValueError("Invalid T-shirt sleeve direction")
        dx, dz = dx / length, dz / length
        # Preserve boundary phase to avoid twisting the sleeve attachment.
        phases = []
        for i in boundary:
            x, y, z = vertices[i]
            phases.append(math.atan2((x - origin[0]) * -dz + (z - origin[2]) * dx,
                                     y - origin[1]))
        previous = boundary
        for step in range(1, 7):
            t = step / 6
            radius = 0.053 * height + ease * 0.65
            points = []
            for i, phase in zip(boundary, phases):
                cuff = (origin[0] + dx * height * 0.14 - dz * radius * math.sin(phase),
                        origin[1] + radius * math.cos(phase),
                        origin[2] + dz * height * 0.14 + dx * radius * math.sin(phase))
                points.append(tuple(a + (b - a) * t for a, b in zip(vertices[i], cuff)))
            current = ring(points)
            join(previous, current)
            previous = current

    # Drop unused interior points of the armhole patches.
    used = sorted({i for face in faces for i in face})
    remap = {old: new for new, old in enumerate(used)}
    return [vertices[i] for i in used], [tuple(remap[i] for i in face) for face in faces]
