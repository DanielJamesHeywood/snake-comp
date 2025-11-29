from dataclasses import dataclass

from external_ai.food import count_food_eaten, food_distance_sum
from external_ai.safety import can_reach_tail, closest_enemy_distance
from snake.logic import GameState, Snake, Turn


@dataclass
class SearchNode:
    snake: Snake
    path: list[Turn]
    score: float


def beam_search(
    state: GameState,
    beam_width: int = 6,
    max_depth: int = 16,
    food_eaten_weight: float = 25.0,
    food_distance_weight: float = 10.0,
    enemy_weight: float = 10.0,
):
    TURNS = [Turn.LEFT, Turn.STRAIGHT, Turn.RIGHT]

    initial_node = SearchNode(
        snake=clone_snake(state.snake),
        path=[],
        score=0.0,
    )

    beam = [initial_node]

    for _ in range(max_depth):
        candidates = []

        for node in beam:
            for turn in TURNS:
                next_head = node.snake.get_next_head(turn)

                if not is_valid_move(state, node.snake, next_head):
                    continue

                new_snake = apply_move(node.snake, turn, next_head, state.food)

                new_path = node.path + [turn]
                path_positions = get_path_positions(state.snake, new_path)

                score = evaluate_node(
                    state,
                    new_snake,
                    path_positions,
                    food_eaten_weight,
                    food_distance_weight,
                    enemy_weight,
                )

                candidates.append(
                    SearchNode(
                        snake=new_snake,
                        path=new_path,
                        score=score,
                    )
                )

        if not candidates:
            break

        candidates.sort(key=lambda n: n.score, reverse=True)
        beam = candidates[:beam_width]

    if beam and beam[0].path:
        return beam[0].path[0]
    
    return None


def is_valid_move(state: GameState, snake: Snake, next_head: tuple[int, int]) -> bool:
    if not (0 <= next_head[0] < state.width and 0 <= next_head[1] < state.height):
        return False
    if next_head in state.walls:
        return False

    body_without_tail = set(list(snake.body)[:-1])
    if next_head in body_without_tail:
        return False

    for enemy in state.enemies:
        if next_head in set(enemy.body):
            return False

    return True


def apply_move(
    snake: Snake, turn: Turn, next_head: tuple[int, int], food: set[tuple[int, int]]
) -> Snake:
    new_snake = clone_snake(snake)
    new_snake.body.appendleft(next_head)
    new_snake.direction = (snake.direction + turn.value) % 4

    if next_head not in food:
        new_snake.body.pop()
    else:
        new_snake.score += 1

    return new_snake


def get_path_positions(initial_snake: Snake, path: list[Turn]) -> list[tuple[int, int]]:
    positions = []
    snake = clone_snake(initial_snake)

    for turn in path:
        next_head = snake.get_next_head(turn)
        positions.append(next_head)
        snake.body.appendleft(next_head)
        snake.body.pop()
        snake.direction = (snake.direction + turn.value) % 4

    return positions


def evaluate_node(
    state: GameState,
    snake: Snake,
    path_positions: list[tuple[int, int]],
    food_eaten_weight: float,
    food_distance_weight: float,
    enemy_weight: float,
) -> float:
    score = 0.0

    head = snake.head
    tail = snake.body[-1]
    walls_tuple = tuple(sorted(state.walls))
    body_tuple = tuple(snake.body)

    can_reach = can_reach_tail(
        head, tail, body_tuple, walls_tuple, state.width, state.height
    )
    if not can_reach:
        score -= 1000.0

    food_eaten = count_food_eaten(path_positions, state.food)
    score += food_eaten * food_eaten_weight

    food_score = food_distance_sum(state, head) * food_distance_weight
    score += food_score

    if state.enemies:
        enemy_dist = closest_enemy_distance(state, head)
        if enemy_dist < 5:
            score -= (5 - enemy_dist) * enemy_weight

    return score


def clone_snake(snake: Snake) -> Snake:
    new_snake = Snake(snake.head[0], snake.head[1], snake.id, snake.direction)
    new_snake.body = snake.body.copy()
    new_snake.score = snake.score
    new_snake.isAlive = snake.isAlive

    return new_snake
