import random as rand
import time as time
from collections import deque


cycle = 1


# Create a job
# jobs          - Jobs queue
# last_job_time - Cycle of the last job Creation
# cur_job_id    - ID of the last job created
# Returns:
#   last_job_time
#   cur_job_id
def create_job(jobs, last_job_time, cur_job_id):
    if rand.randint(1, 10) < (cycle - last_job_time):
        new_job = []
        new_job.append(cur_job_id)
        new_job.append(cycle)
        new_job.append(rand.randint(1, 12) * 5)
        new_job.append(rand.randint(5, 30))
        jobs.append(new_job)
        return cycle, cur_job_id + 1
    return last_job_time, cur_job_id


# Manage jobs, delete jobs, ready jobs
# memory        - The state of the memory
# jobs          - Jobs queue
# fit_type      - Number to represent the fit type
# ready_queue   - The queue of jobs ready to be worked on
def manage_jobs(memory, jobs, fit_type, ready_queue):
    if len(jobs) > 0:
        new_job_id = False
        if fit_type == 0:
            new_job_id = first_fit(memory, jobs)
        elif fit_type == 1:
            new_job_id = best_fit(memory, jobs)
        elif fit_type == 2:
            new_job_id = worst_fit(memory, jobs)

        if new_job_id:
            ready_queue.append([new_job_id, 0])


# Put job in next available fit
# memory - The state of the memory
# jobs - Jobs queue
# Returns:
#   new job ID or False
def first_fit(memory, jobs):
    for y in range (len(jobs)):
        next_job = jobs[y]
        new_job_id = next_job[0]
        for x in range(len(memory)):
            cur_cell = memory[x]
            if cur_cell[0] == -1:
                if cur_cell[3] == next_job[3]:
                    jobs.remove(next_job)
                    memory[x] = next_job
                    return new_job_id
                elif cur_cell[3] > next_job[3]:
                    memory[x + next_job[3]][0] = -1
                    memory[x + next_job[3]][3] = cur_cell[3] - next_job[3]
                    jobs.remove(next_job)
                    memory[x] = next_job
                    return new_job_id

    return False


# Put job in best available fit
# memory - The state of the memory
# jobs - Jobs queue
# Returns:
#   new job ID or False
def best_fit(memory, jobs):
    for y in range(len(jobs)):
        next_job = jobs[y]
        new_job_id = next_job[0]
        least_cell = -1
        least_cell_values = []
        for x in range(len(memory)):
            cur_cell = memory[x]
            if cur_cell[0] == -1:
                if cur_cell[3] == next_job[3]:
                    jobs.remove(next_job)
                    memory[x] = next_job
                    return new_job_id
                elif cur_cell[3] > next_job[3] and (least_cell == -1 or cur_cell[3] < least_cell_values[3]):
                    least_cell = x
                    least_cell_values = cur_cell
        if not least_cell == -1:
            memory[least_cell + next_job[3]][0] = -1
            memory[least_cell + next_job[3]][3] = least_cell_values[3] - next_job[3]
            jobs.remove(next_job)
            memory[least_cell] = next_job
            return new_job_id

    return False


# Put job in worst available fit
# memory - The state of the memory
# jobs - Jobs queue
# Returns:
#   new job ID or False
def worst_fit(memory, jobs):
    for y in range(len(jobs)):
        next_job = jobs[0]
        new_job_id = next_job[0]
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
                jobs.remove(next_job)
                memory[biggest_cell] = next_job
                return new_job_id
            else:
                memory[biggest_cell + next_job[3]][0] = -1
                memory[biggest_cell + next_job[3]][3] = biggest_cell_values[3] - next_job[3]
                jobs.remove(next_job)
                memory[biggest_cell] = next_job
                return new_job_id

    return False


# Process the process and clear memory of finished processes
# memory - The state of the memory
# ready_queue - The queue of jobs ready to be worked on
# jobs_processed - The count of jobs processed
# avg_time_figures - The table for average timers
# Returns:
#   num_of_occupied (Statistics)
#   num_of_holes (Statistics)
#   total_occupied_size (Statistics)
#   total_holes_size (Statistics)
#   avg_time_figures (Statistics)
#   jobs_processed (Statistics)
def process_memory(memory, ready_queue, jobs_processed, avg_time_figures):

    num_of_occupied = 0
    num_of_holes = 0
    total_occupied_size = 0
    total_holes_size = 0

    size_of_last_hole_if_free = 0
    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] > 0:

            # Statistics For Occupied Cells
            num_of_occupied = num_of_occupied + 1
            total_occupied_size = total_occupied_size + cur_cell[3]

            if cur_cell[0] == ready_queue[0][0]:
                if cur_cell[2] < 1:
                    # If we are in the polling period, begin taking processing statistics
                    if cycle > 1000:
                        jobs_processed = jobs_processed + 1
                        avg_time_figures[0] = avg_time_figures[0] + (((cycle - cur_cell[1]) - avg_time_figures[0]) / jobs_processed)
                    cur_cell = [-1, 0, 0, cur_cell[3]]

                    # Coelescence
                    if x + cur_cell[3] < 175 and memory[x + cur_cell[3]][0] == -1:
                        old_cell_size = cur_cell[3]
                        cur_cell[3] = cur_cell[3] + memory[x + cur_cell[3]][3]
                        memory[x + old_cell_size] = [0, 0, 0, 0]
                    if size_of_last_hole_if_free > 0:
                        memory[x - size_of_last_hole_if_free][3] = size_of_last_hole_if_free + cur_cell[3]
                        cur_cell = [0, 0, 0, 0]

                    # Remove job from ready_queue
                    ready_queue.popleft()
                else:
                    cur_cell[2] = cur_cell[2] - 1

                    # Rotate the ready_queue, Round Robin style
                    ready_queue[0][1] = ready_queue[0][1] + 1
                    if ready_queue[0][1] >= 5:
                        ready_queue[0][1] = 0
                        ready_queue.append(ready_queue.popleft())

                memory[x] = cur_cell

            # Jump forward to the next cell
            x = x + cur_cell[3]

            # This hole is not free so don't save its size for coelescence
            size_of_last_hole_if_free = 0

        elif cur_cell[0] < 0:

            # Statistics For Holes
            num_of_holes = num_of_holes + 1
            total_holes_size = total_holes_size + cur_cell[3]

            # Jump forward to the next cell
            x = x + cur_cell[3]

            # This hole is free, so save its size for coelescence
            size_of_last_hole_if_free = cur_cell[3]

    return num_of_occupied, num_of_holes, total_occupied_size, total_holes_size, avg_time_figures, jobs_processed


# Main function
#
# Jacob Schlecht
# CS4323
# Simulation Project, Phase 2
# 23/10/2017
# fit_type - The requested memory management style, 0-2
def main(fit_type):

    # Operating System Variables
    memory = []
    memory.append([-1, 0, 0, 175])
    jobs = []
    ready_queue = deque([])
    global cycle
    cycle = 1
    last_job_time = 0
    cur_job_id = 1
    jobs_processed = 0

    # Statistics Variables
    # Time tuple, [avg turnaround, avg wait time, avg process time]
    avg_time_figures = [0.0, 0.0, 0.0]

    for x in range(174):
        memory.append([0, 0, 0, 0])

    # Clock Cycle Simulation
    while cycle < 5000:
        cycle = cycle + 1

        # Job Creation
        if len(jobs) < 100:
            last_job_time, cur_job_id = create_job(jobs, last_job_time, cur_job_id)

        # Job Managment
        manage_jobs(memory, jobs, fit_type, ready_queue)

        # Keep track of longest waiting process and process current process
        num_of_occupied, num_of_holes, total_occupied_size, total_holes_size, avg_time_figures, jobs_processed = \
            process_memory(memory, ready_queue, jobs_processed, avg_time_figures)


        # Statistic Printing
        if cycle > 1000:
            if cycle%200 == 0:
                avg_occupied_size = 0.0
                if num_of_occupied > 0:
                    avg_occupied_size = float(total_occupied_size) / num_of_occupied
                print 'VTU-' + str(cycle) + ' Ocupied Blocks: ' + str(num_of_occupied) + ' Average Size: ' + '%.4f' % (avg_occupied_size*10) + 'K'
            if cycle%300 == 0:
                avg_hole_size = 0.0
                if num_of_holes > 0:
                    avg_hole_size = float(total_holes_size) / num_of_holes
                print 'VTU-' + str(cycle) + ' Free Blocks: ' + str(num_of_holes) + ' Average Size: ' + '%.4f' % (avg_hole_size*10) + 'K'
            if cycle%500 == 0:
                external_fragmentation = total_holes_size * 10
                print 'VTU-' + str(cycle) + ' ' + str(external_fragmentation) + 'K Byte Fragmentation'

    print 'Average Turnaround: ' + '%.4f' % avg_time_figures[0]
    print 'Average Wait Time: ' + '%.4f' % avg_time_figures[1]
    print 'Average Processing Time: ' + '%.4f' % avg_time_figures[2]


print '---------------------FIRST FIT------------------------'
main(0)
print '----------------------BEST FIT------------------------'
main(1)
print '---------------------WORST FIT------------------------'
main(2)
print '------------------------DONE--------------------------'
