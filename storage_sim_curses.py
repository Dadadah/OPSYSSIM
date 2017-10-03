import random as rand
import time
import curses
from curses import wrapper
from collections import deque


cycle = 1


# Create a jobs
# jobs          - Jobs queue
# last_job_time - Cycle of the last job Creation
# last_job      - Last job created, for UI
# cur_job_id    - ID of the last job created
# Returns:
#   last_job_time
#   last_job
#   cur_job_id
def create_job(jobs, last_job_time, last_job, cur_job_id):
    if rand.randint(1, 10) < (cycle - last_job_time):
        new_job = []
        new_job.append(cur_job_id)
        new_job.append(cycle)
        new_job.append(rand.randint(1, 12) * 5)
        new_job.append(rand.randint(5, 30))
        jobs.append(new_job)
        return cycle, new_job, cur_job_id + 1
    return last_job_time, last_job, cur_job_id


# Manage jobs, delete jobs, ready jobs
# memory        - The state of the memory
# jobs          - Jobs queue
# rejected_jobs - The count of rejected jobs
# visual_memory - Visual representation of memory for UI
# fit_type      - Number to represent the fit type
# Returns:
#   rejected_jobs
def manage_jobs(memory, jobs, rejected_jobs, visual_memory, fit_type):
    if len(jobs) > 0:
        # Finding Biggest Block
        biggest_block = [0, 0, 0, 0]
        for x in range(len(memory)):
            cur_cell = memory[x]
            if not cur_cell[0] == 0:
                if cur_cell[3] > biggest_block[3]:
                    biggest_block = cur_cell
        # Reject Oversized Jobs
        next_job = jobs[0]
        while next_job[3] > biggest_block[3] and not len(jobs) <= 0:
            rejected_jobs = rejected_jobs + 1
            jobs.popleft()
            if len(jobs) > 0:
                next_job = jobs[0]
        if len(jobs) > 0:
            if fit_type == 0:
                first_fit(memory, jobs, visual_memory)
            elif fit_type == 1:
                best_fit(memory, jobs, visual_memory)
            elif fit_type == 2:
                worst_fit(memory, jobs, visual_memory)
    return rejected_jobs


# Put job in next available fit
# memory - The state of the memory
# jobs - Jobs queue
# visual_memory - Visual representation of memory for UI
def first_fit(memory, jobs, visual_memory):
    next_job = jobs[0]
    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] == -1:
            if cur_cell[3] == next_job[3]:
                memory[x] = jobs.popleft()
                for y in range(next_job[3]):
                    visual_memory[x + y] = '#'
                return
            elif cur_cell[3] > next_job[3]:
                memory[x + next_job[3]][0] = -1
                memory[x + next_job[3]][3] = cur_cell[3] - next_job[3]
                memory[x] = jobs.popleft()
                for y in range(next_job[3]):
                    visual_memory[x + y] = '#'
                return


# Put job in best available fit
# memory - The state of the memory
# jobs - Jobs queue
# visual_memory - Visual representation of memory for UI
def best_fit(memory, jobs, visual_memory):
    next_job = jobs[0]
    least_cell = -1
    least_cell_values = []
    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] == -1:
            if cur_cell[3] == next_job[3]:
                memory[x] = jobs.popleft()
                for y in range(next_job[3]):
                    visual_memory[x + y] = '#'
                return
            elif cur_cell[3] > next_job[3] and (least_cell == -1 or cur_cell[3] < least_cell_values[3]):
                least_cell = x
                least_cell_values = cur_cell
    if not least_cell == -1:
        memory[least_cell + next_job[3]][0] = -1
        memory[least_cell + next_job[3]][3] = least_cell_values[3] - next_job[3]
        memory[least_cell] = jobs.popleft()
        for y in range(next_job[3]):
            visual_memory[least_cell + y] = '#'
        return


# Put job in worst available fit
# memory - The state of the memory
# jobs - Jobs queue
# visual_memory - Visual representation of memory for UI
def worst_fit(memory, jobs, visual_memory):
    next_job = jobs[0]
    biggest_cell = -1
    biggest_cell_values = []
    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] == -1:
            if cur_cell[3] >= next_job[3] and (biggest_cell == -1 or cur_cell[3] > biggest_cell_values[3]):
                biggest_cell = x
                biggest_cell_values = cur_cell
    if not biggest_cell == -1:
        if biggest_cell_values[3] == next_job[3]:
            memory[biggest_cell] = jobs.popleft()
        else:
            memory[biggest_cell + next_job[3]][0] = -1
            memory[biggest_cell + next_job[3]][3] = biggest_cell_values[3] - next_job[3]
            memory[biggest_cell] = jobs.popleft()
        for y in range(next_job[3]):
            visual_memory[biggest_cell + y] = '#'


# Process the process and clear memory of finished processes
# memory - The state of the memory
# current_job - The ID of the job we are processing currently
# jobs_processed - The count of jobs processed
# avg_turnaround - The average turnaround time for processes
# visual_memory - Visual representation of memory for UI
# Returns:
#   current_job
#   num_of_occupied (Statistics)
#   num_of_holes (Statistics)
#   total_occupied_size (Statistics)
#   total_holes_size (Statistics)
#   avg_turnaround (Statistics)
#   jobs_processed (Statistics)
def process_memory(memory, current_job, jobs_processed, avg_turnaround, visual_memory):
    lowest_time = [5000, -1]

    num_of_occupied = 0
    num_of_holes = 0
    total_occupied_size = 0
    total_holes_size = 0

    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] > 0:

            # Statistics For Occupied Cells
            num_of_occupied = num_of_occupied + 1
            total_occupied_size = total_occupied_size + cur_cell[3]

            if cur_cell[0] == current_job:
                if cur_cell[2] < 1:
                    # If we are in the polling period, begin taking statistics
                    if cycle > 1000:
                        jobs_processed = jobs_processed + 1
                        avg_turnaround = avg_turnaround + (((cycle - cur_cell[1]) - avg_turnaround) / jobs_processed)
                    cur_cell = [-1, 0, 0, cur_cell[3]]
                    for y in range(cur_cell[3]):
                        visual_memory[x + y] = '-'
                else:
                    lowest_time = [cur_cell[1], cur_cell[0]]
                cur_cell[2] = cur_cell[2] - 1
                memory[x] = cur_cell
                current_job = -1
            else:
                if cur_cell[1] < lowest_time[0]:
                    lowest_time = [cur_cell[1], cur_cell[0]]
        elif cur_cell[0] < 0:

            # Statistics For Holes
            num_of_holes = num_of_holes + 1
            total_holes_size = total_holes_size + cur_cell[3]

    current_job = lowest_time[1]

    return current_job, num_of_occupied, num_of_holes, total_occupied_size, total_holes_size, avg_turnaround, jobs_processed


def main(stdscr, fit_type):
    # Curses initialization
    curses.noecho()
    stdscr.clear()

    # GUI Elements
    last_job = [0, 0, 0, 0]
    visual_memory = []
    visual_memory.append('-')

    # Operating System Variables
    memory = []
    memory.append([-1, 0, 0, 175])
    jobs = deque([])
    # cycle = 1
    global cycle
    cycle = 1
    last_job_time = 0
    cur_job_id = 1
    current_job = 1
    jobs_processed = 0

    # Statistics Variables
    avg_turnaround = 0.0
    rejected_jobs = 0

    for x in range(174):
        memory.append([0, 0, 0, 0])
        visual_memory.append('-')

    # Clock Cycle Simulation
    while cycle < 5000:
        cycle = cycle + 1

        # Clear the screen to prevent overflow/overwrite
        stdscr.clear()

        # Job Creation
        last_job_time, last_job, cur_job_id = create_job(jobs, last_job_time, last_job, cur_job_id)

        # Job Managment
        rejected_jobs = manage_jobs(memory, jobs, rejected_jobs, visual_memory, fit_type)

        # Keep track of longest waiting process and process current process
        current_job, num_of_occupied, num_of_holes, total_occupied_size, total_holes_size, avg_turnaround, jobs_processed = \
            process_memory(memory, current_job, jobs_processed, avg_turnaround, visual_memory)

        # Set Up Visual Variables
        top_job = 'None'
        avg_occupied_size = 0.0
        avg_hole_size = 0.0
        if len(jobs) > 0:
            top_job = str(jobs[0])
        if num_of_occupied > 0:
            avg_occupied_size = float(total_occupied_size) / num_of_occupied
        if num_of_holes > 0:
            avg_hole_size = float(total_holes_size) / num_of_holes

        # Set Up Visuals
        stdscr.addstr(0, 0,    'Memory:')
        stdscr.addstr(1, 0,    ''.join(visual_memory))
        stdscr.addstr(8, 0,    'Cycle:                           ' + str(cycle))
        stdscr.addstr(10, 0,   'Job added to queue:              ' + str(last_job))
        stdscr.addstr(11, 0,   'Job on top of queue:             ' + top_job)
        stdscr.addstr(12, 0,   'Jobs in queue:                   ' + str(len(jobs)))
        stdscr.addstr(15, 0,   'Average Turnaround:              ' + '%.4f' % avg_turnaround)
        stdscr.addstr(16, 0,   'Processes in memory:             ' + str(num_of_occupied))
        stdscr.addstr(17, 0,   'Holes:                           ' + str(num_of_holes))
        stdscr.addstr(18, 0,   'Average Occupied Size:           ' + '%.4f' % avg_occupied_size)
        stdscr.addstr(19, 0,   'Average Hole Size:               ' + '%.4f' % avg_hole_size)
        stdscr.addstr(20, 0,   'Rejected Jobs:                   ' + str(rejected_jobs))
        stdscr.refresh()
        time.sleep(0.005)

    # Curses end
    fit_type_string = ''
    if fit_type == 0:
        fit_type_string = 'First Fit'
    elif fit_type == 1:
        fit_type_string = 'Best Fit'
    elif fit_type == 2:
        fit_type_string = 'Worst Fit'
    stdscr.addstr(23, 0, 'Simulation for ' + fit_type_string + ' complete, press any key to continue.')
    stdscr.getch()
    curses.echo()
    curses.endwin()


wrapper(main, 0)
wrapper(main, 1)
wrapper(main, 2)
