from simulation.obstacle import Obstacle
from simulation.simulated_robot import SimulatedRobot
from simulation.environment import Environment

import pygame
import math

def draw_robot(screen, robot):
    """
    Draw the robot and the direction indicator on the given Pygame screen.
    """
    x, y = robot.get_position()
    orientation = robot.get_orientation()

    robot_size = 20
    direction_length = 30

    pygame.draw.circle(screen, (118, 173, 100), (int(x), int(y)), robot_size)

    angle = math.radians(orientation)

    end_x = x + direction_length * math.cos(angle)
    end_y = y - direction_length * math.sin(angle)

    pygame.draw.line(screen, (118, 173, 100), (int(x), int(y)), (int(end_x), int(end_y)), 4)

def draw_obstacle(screen, obstacle):
    """
    Draw the obstacle on the given Pygame screen.
    """
    pygame.draw.rect(screen, (0, 0, 0), (obstacle.x, obstacle.y, obstacle.width, obstacle.height))

def main():
    """
    Main function to run the simulation.
    """
    environment = Environment(800, 600)

    obstacle1 = Obstacle(200, 150, 100, 50)
    obstacle2 = Obstacle(500, 300, 75, 150)

    environment.add_obstacle(obstacle1)
    environment.add_obstacle(obstacle2)

    robot = SimulatedRobot()

    pygame.init()

    screen = pygame.display.set_mode((environment.width, environment.height))
    pygame.display.set_caption("Autonomous Plant Care System")

    clock = pygame.time.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))

        for obstacle in environment.get_obstacles():
            draw_obstacle(screen, obstacle)

        draw_robot(screen, robot)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()