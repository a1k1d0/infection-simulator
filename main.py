import pygame
import sys
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from uuid import uuid4


# The human class that represents each dot on the board
class Human:
    def __init__(self, x, y, radius, color, is_infected=False):
        # position, size, color and speed
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel = 15  # Velocity

        # If they are infected and at what time they were
        self.is_infected = is_infected
        self.time_infected = 0

        # If they are immune and at what time they were
        self.is_immune = False
        self.time_immunised = 0

        # Used to calculate when they get vaccinated if they get vaccinated
        self.is_vaccinated = False
        self.vaccination_timestamp = 0

        # If they are dead
        self.is_dead = False

    # Drawing the cirlce
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    # Moving the circle
    def move(self):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        if 0 < self.x + dx * self.vel < 800:
            self.x += dx * self.vel
        if 0 < self.y + dy * self.vel < 600:
            self.y += dy * self.vel


def handle_infection(human, people, simulation_time, time_to_immune, mortality_rate):
    """This function handles the death of a human,
       the immunisation of a sick human contaminating another human

    Args:
        human (Class): The given human in the population (people) set
        people (List): A list of humans representing the population
        simulation_time (float): Represents the in game time that has passed
        time_to_immune (float): Represents the time it takes for a sick individual
                                to become immmune (or die)
        mortality_rate (float): The amount (percentage) of people that die at the
                                end of their sickness
    """
    if human.is_infected:
        if simulation_time - human.time_infected > time_to_immune:
            death_roll = random.random()

            if death_roll > mortality_rate:
                human.is_infected = False
                human.color = (0, 0, 255)
                human.is_immune = True
                human.time_immunised = simulation_time
            else:
                human.is_dead = True
                human.color = (155, 155, 155)
                human.vel = 0
                human.is_infected = False
                human.is_immunised = False

        else:
            human.color = (255, 0, 0)
            for other_human in people:
                if (
                    other_human != human
                    and not other_human.is_immune
                    and not other_human.is_infected
                    and not other_human.is_dead
                ):
                    if (human.x - other_human.x) ** 2 < 10**2 and (
                        human.y - other_human.y
                    ) ** 2 < 10**2:
                        other_human.is_infected = True
                        other_human.time_infected = simulation_time


def count_population_states(people):
    """Counts the different catagories in the population

    Args:
        people (list): a list of humans representing the entire population

    Returns:
        set: the 4 different catagoires, infected, uninfected, immune and dead
    """
    number_of_infected_people = sum(human.is_infected for human in people)
    number_of_uninfected_people = sum(
        not human.is_infected and not human.is_immune and not human.is_dead
        for human in people
    )
    number_of_immune_people = sum(human.is_immune for human in people)
    number_of_dead_people = sum(human.is_dead for human in people)
    return (
        number_of_infected_people,
        number_of_uninfected_people,
        number_of_immune_people,
        number_of_dead_people,
    )


def create_population(amount_of_people, width, height):
    """Sets up the entire population

    Args:
        amount_of_people (int): The amount of people in the population
        width (int): screen width
        height (int): screen height

    Returns:
        list: the population list filled with human objects
    """
    return [
        Human(random.randrange(width), random.randrange(height), 5, (0, 255, 0))
        for _ in range(amount_of_people)
    ]


def write_data_to_csv(data, filename):
    """Writes the data to a csv

    Args:
        data (list): a list with all the data for every itteration
    """
    with open(filename, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in data:
            csvwriter.writerow(row)


def plot_data(data):
    """plots the data in matplot lib

    Args:
        data (list): data for every itteration
    """
    # Prepare your data for matplotlib
    time = [row[0] for row in data[1:]]  # Skip the header
    infected = [row[1] for row in data[1:]]
    uninfected = [row[2] for row in data[1:]]
    immune = [row[3] for row in data[1:]]
    dead = [row[4] for row in data[1:]]

    plt.plot(time, infected, label="Infected", color="red")
    plt.plot(time, uninfected, label="Uninfected", color="green")
    plt.plot(time, immune, label="Immune", color="blue")
    plt.plot(time, dead, label="Dead", color="gray")

    plt.legend()
    # Show the plot
    plt.show()


def vaccinate_population(
    people, vaccination_limit, vaccination_percent, adoption_rate, current_time
):
    """This function vaccinates the population at a given time

    Args:
        vaccination_limit (int): the amount of people either infected or immune before vaccination begins
        vaccination_percent (float): the percentage of people that get vaccinated
        adoption_rate (int): the time in seconds it takes for everyone that want to get vaccinated get vaccinated

    Returns:
        bool: used to check so that the vaccination only runs once
    """
    infected_or_immune = sum((human.is_infected or human.is_immune) for human in people)
    if infected_or_immune >= vaccination_limit:
        to_be_vaccinated = int(len(people) * vaccination_percent)
        for human in random.sample(people, to_be_vaccinated):
            human.vaccination_timestamp = current_time + random.uniform(
                0, adoption_rate
            )
        return False
    else:
        return True


def update_human_status(human, simulation_time):
    """Updates a given human so they actually get vaccinated

    Args:
        human (class): the human in question
        simulation_time (float): in game time
    """
    if human.vaccination_timestamp and human.vaccination_timestamp <= simulation_time:
        if human.is_infected == False:
            human.is_immune = True
            human.color = (0, 0, 255)
            human.is_vaccinated = True
            human.vaccination_timestamp = 0


def loss_of_immunisation(human, simulation_time, immunisation_length):
    if not human.is_vaccinated and not human.is_dead:
        if simulation_time - human.time_immunised > immunisation_length:
            human.is_immune = False
            human.color = (0, 255, 0)


def main():
    # init pygame
    pygame.init()

    # Set some semi-global variables
    width, height = 800, 600
    fps = 10
    tick = 0
    no_vaccination = True

    # These are the variables you can tweak
    amount_of_people = 500
    time_to_immune = 3
    vaccination_limit = 150
    vaccination_percent = 0.7
    adoption_rate = 10
    mortality_rate = 0.1
    immunisation_length = 10

    # Setting the screen and the in game clock
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # creats the population and adds the first infected human
    people = create_population(amount_of_people - 1, width, height)
    people.append(Human(width // 2, height // 2, 5, (0, 255, 0), True))

    # Creates the first line of the data list used for the csv
    data = [
        [
            "Time",
            "Number of infected people",
            "Number of uninfected people",
            "number of immune people",
            "number of dead people",
        ]
    ]

    # Main simulation loop
    while True:
        clock.tick(fps)

        # Sets the in game time
        simulation_time = tick / fps

        # Handles the quiting of the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Runs as long as there has not been a vaccination
        if no_vaccination:
            no_vaccination = vaccinate_population(
                people,
                vaccination_limit,
                vaccination_percent,
                adoption_rate,
                simulation_time,
            )

        # Updates movement, vaccination, immunisation, infection and death for each human
        for human in people:
            human.move()
            update_human_status(human, simulation_time)
            loss_of_immunisation(human, simulation_time, immunisation_length)
            handle_infection(
                human, people, simulation_time, time_to_immune, mortality_rate
            )

        # counts the amount in each catagory and then adds it to the data varaible
        infected, uninfected, immune, dead = count_population_states(people)
        data.append([simulation_time, infected, uninfected, immune, dead])

        # if there are no more infected write the data to a csv plot the data and the quit
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

        # Draw the screen and humans
        screen.fill((0, 0, 0))
        for human in people:
            human.draw(screen)
        pygame.display.flip()

        # add a tick and print the simulation time
        tick += 1
        print(simulation_time)


if __name__ == "__main__":
    main()
