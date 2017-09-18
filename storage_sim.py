import random as rand
import time
import curses
from collections import deque


def main():
    # Curses initialization
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.clear()

    # GUI Elements
    last_job = [0, 0, 0, 0]
    visual_memory = []
    visual_memory.append('O')

    # Operating System Variables
    memory = []
    memory.append([-1, 0, 0, 175])
    jobs = deque([])
    cycle = 0
    last_process = 0
    cur_job_id = 1
    current_job = 1
    jobs_processed = 0

    # Statistics Variables
    avg_turnaround = 0.0

    for x in range(174):
        memory.append([0, 0, 0, 0])
        visual_memory.append('-')

    # Clock Cycle Simulation
    while cycle <= 5000:
        cycle = cycle + 1

        # Cycle Dependent Statistics
        num_of_holes = 0

        # Job Creation
        if rand.randint(1, 10) < (cycle - last_process):
            new_job = []
            new_job.append(cur_job_id)
            new_job.append(cycle)
            new_job.append(rand.randint(1, 12) * 5)
            new_job.append(rand.randint(5, 30))
            jobs.append(new_job)
            last_process = cycle
            cur_job_id = cur_job_id + 1
            last_job = new_job
        # Job Managment
        if len(jobs) > 0:
            # Finding Biggest Block
            biggest_block = [0, 0, 0, 0]
            next_job = jobs[0]
            for x in range(len(memory)):
                cur_cell = memory[x]
                if not cur_cell[0] == 0:
                    if cur_cell[3] > biggest_block[3]:
                        biggest_block = cur_cell
            # Rejecting Oversized Jobs
            while next_job[3] > biggest_block[3] and not len(jobs) <= 0:
                jobs.popleft()
                next_job = jobs[0]
            # First Fit
            for x in range(len(memory)):
                cur_cell = memory[x]
                if cur_cell[0] == -1:
                    if cur_cell[3] == next_job[3]:
                        memory[x] = jobs.popleft()
                        for y in range(next_job[3]):
                            visual_memory[x + y] = '#'
                        break
                    elif cur_cell[3] > next_job[3]:
                        memory[x + next_job[3]][0] = -1
                        memory[x + next_job[3]][3] = cur_cell[3] - next_job[3]
                        memory[x] = jobs.popleft()
                        for y in range(next_job[3]):
                            visual_memory[x + y] = '#'
                        break
        # Keep Track of Longest Waiting Process
        lowest_time = [5000, -1]
        for x in range(len(memory)):
            cur_cell = memory[x]
            if cur_cell[0] > 0:

                # Statistics
                num_of_holes = num_of_holes + 1

                if cur_cell[0] == current_job:
                    if cur_cell[2] < 1:
                        if cur_cell[1] > 1000:
                            jobs_processed = jobs_processed + 1
                            avg_turnaround = avg_turnaround + \
                                (((cycle - cur_cell[1]) - avg_turnaround)
                                 / jobs_processed)
                        cur_cell = [-1, 0, 0, cur_cell[3]]
                        for y in range(cur_cell[3]):
                            visual_memory[x + y] = '-'
                    cur_cell[2] = cur_cell[2] - 1
                    memory[x] = cur_cell
                    current_job = -1
                else:
                    if cur_cell[1] < lowest_time[0]:
                        lowest_time = [cur_cell[1], cur_cell[0]]
            elif cur_cell[0] < 0:
                # Statistics
                num_of_holes = num_of_holes + 1
        # If We Have No Job, Assign Job
        if current_job == -1:
            current_job = lowest_time[1]

        # Set Up Visuals
        stdscr.addstr(0, 0, 'Memory:')
        stdscr.addstr(1, 0, ''.join(visual_memory))
        stdscr.addstr(10, 0, 'Job added to queue: ' + str(last_job))
        stdscr.addstr(10, 50, 'Jobs in queue: ' + str(len(jobs)))
        if len(jobs) > 0:
            stdscr.addstr(10, 100, 'Job on top of queue: ' + str(jobs[0]))
        stdscr.addstr(15, 0, 'Average Turnaround: ' + str(avg_turnaround))
        stdscr.addstr(16, 0, 'Holes: ' + str(num_of_holes))
        stdscr.addstr(17, 0, 'Average Hole Size: ' + str(175./num_of_holes))
        stdscr.refresh()
        stdscr.clear()
        time.sleep(0.01)

    # Curses end
    curses.echo()
    curses.endwin()


main()
