from simulation.simulated_robot import SimulatedRobot
from simulation.environment import Environment

import pygame

def draw_robot(screen, robot):
    """
    Draw the robot on the given Pygame screen.
    """
    x, y = robot.get_position()

    robot_size = 20

    pygame.draw.circle(screen, (0, 0, 255), (int(x), int(y)), robot_size)

def main():
    """
    Main function to run the simulation.
    """
    environment = Environment(800, 600)
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
        draw_robot(screen, robot)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()