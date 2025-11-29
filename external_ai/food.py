from snake.logic import GameState


def food_distance_sum(state: GameState, head: tuple[int, int]) -> float:
    if not state.food:
        return 0.0

    total = 0.0
    for food in state.food:
        dist = abs(food[0] - head[0]) + abs(food[1] - head[1])
        if dist > 0:
            total += 1.0 / dist

    return total


def count_food_eaten(path: list[tuple[int, int]], food: set[tuple[int, int]]) -> int:
    return sum(1 for pos in path if pos in food)
