from collections import deque
from functools import lru_cache

from snake.logic import GameState


@lru_cache(maxsize=10000)
def can_reach_tail(
    head: tuple[int, int],
    tail: tuple[int, int],
    body_tuple: tuple[tuple[int, int], ...],
    walls_tuple: tuple[tuple[int, int], ...],
    width: int,
    height: int,
) -> bool:
    if head == tail:
        return True

    body_list = list(body_tuple)
    body_index = {pos: i for i, pos in enumerate(body_list)}
    snake_length = len(body_list)
    obstacles = set(walls_tuple) | {head}

    visited = {head}
    queue = deque([(head, 0)])

    while queue:
        (x, y), dist = queue.popleft()

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny)
            next_dist = dist + 1

            if next_pos == tail:
                return True

            if next_pos in visited:
                continue
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if next_pos in obstacles:
                continue

            if next_pos in body_index:
                segment_index = body_index[next_pos]
                if next_dist <= snake_length - 1 - segment_index:
                    continue

            visited.add(next_pos)
            queue.append((next_pos, next_dist))

    return False


def closest_enemy_distance(state: GameState, head: tuple[int, int]) -> float:
    if not state.enemies:
        return float("inf")

    min_dist = float("inf")
    for enemy in state.enemies:
        dist = abs(enemy.head[0] - head[0]) + abs(enemy.head[1] - head[1])
        if dist < min_dist:
            min_dist = dist

    return min_dist
