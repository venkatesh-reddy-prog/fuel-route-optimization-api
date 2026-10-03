from routing.services.geo import build_route_distances


coordinates = [
    [-86.802566, 33.520625],
    [-86.802585, 33.520655],
    [-86.802638, 33.520736],
    [-86.802690, 33.520811],
]


points = build_route_distances(coordinates)

for point in points:
    print(point)