import pygame
import sys
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from uuid import uuid4


class Human:
    def __init__(self, x, y, radius, color, is_touched=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.is_touched = is_touched
        self.time_infected = 0
        self.is_immune = False
        self.time_immunised = 0
        self.vel = 15  # Velocity

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        if 0 < self.x + dx * self.vel < 800:
            self.x += dx * self.vel
        if 0 < self.y + dy * self.vel < 600:
            self.y += dy * self.vel


def handle_infection(human, people, simulation_time, time_to_immune):
    if human.is_touched:
        if simulation_time - human.time_infected > time_to_immune:
            human.is_touched = False
            human.color = (0, 0, 255)
            human.is_immune = True
            human.time_immunised = simulation_time
        else:
            human.color = (255, 0, 0)
            for other_human in people:
                if (
                    other_human != human
                    and not other_human.is_immune
                    and not other_human.is_touched
                ):
                    if (human.x - other_human.x) ** 2 < 20**2 and (
                        human.y - other_human.y
                    ) ** 2 < 20**2:
                        other_human.is_touched = True
                        other_human.time_infected = simulation_time


def count_population_states(people):
    number_of_infected_people = sum(human.is_touched for human in people)
    number_of_uninfected_people = sum(
        not human.is_touched and not human.is_immune for human in people
    )
    number_of_immune_people = sum(human.is_immune for human in people)
    return (
        number_of_infected_people,
        number_of_uninfected_people,
        number_of_immune_people,
    )


def create_population(amount_of_people, width, height):
    return [
        Human(random.randrange(width), random.randrange(height), 10, (0, 255, 0))
        for _ in range(amount_of_people)
    ]


def write_data_to_csv(data, filename):
    with open(filename, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in data:
            csvwriter.writerow(row)


def plot_data(data):
    # Prepare your data for matplotlib
    time = [row[0] for row in data[1:]]  # Skip the header
    infected = [row[1] for row in data[1:]]
    uninfected = [row[2] for row in data[1:]]
    immune = [row[3] for row in data[1:]]

    plt.plot(time, infected, label="Infected", color="red")
    plt.plot(time, uninfected, label="Uninfected", color="green")
    plt.plot(time, immune, label="Immune", color="blue")

    plt.legend()
    # Show the plot
    plt.show()


def main():
    pygame.init()

    width, height = 800, 600
    fps = 10
    amount_of_people = 50
    time_to_immune = 10
    tick = 0

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    people = create_population(amount_of_people - 1, width, height)
    people.append(Human(width // 2, height // 2, 10, (0, 255, 0), True))

    data = [
        [
            "Time",
            "Number of infected people",
            "Number of uninfected people",
            "number of immune people",
        ]
    ]

    while True:
        clock.tick(fps)
        simulation_time = tick / fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for human in people:
            human.move()
            handle_infection(human, people, simulation_time, time_to_immune)

        infected, uninfected, immune = count_population_states(people)
        data.append([simulation_time, infected, uninfected, immune])

        if infected == 0:
            filename = (
                "people-size"
                + str(amount_of_people)
                + "-immune-time"
                + str(time_to_immune)
                + datetime.now().strftime("%Y%m-%d%H-%M%S-")
                + str(uuid4())
                + ".csv"
            )
            write_data_to_csv(data, filename)
            plot_data(data)
            pygame.quit()
            sys.exit()

        screen.fill((0, 0, 0))
        for human in people:
            human.draw(screen)
        pygame.display.flip()

        tick += 1
        print(simulation_time)


if __name__ == "__main__":
    main()
