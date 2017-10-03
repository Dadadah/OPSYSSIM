import random as rand
from collections import deque


cycle = 1


# Create a jobs
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
# Returns:
#   rejected_jobs
def manage_jobs(memory, jobs, fit_type):
    rejected_jobs = 0
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
                first_fit(memory, jobs)
            elif fit_type == 1:
                best_fit(memory, jobs)
            elif fit_type == 2:
                worst_fit(memory, jobs)
    return rejected_jobs


# Put job in next available fit
# memory - The state of the memory
# jobs - Jobs queue
def first_fit(memory, jobs):
    next_job = jobs[0]
    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] == -1:
            if cur_cell[3] == next_job[3]:
                memory[x] = jobs.popleft()
                return
            elif cur_cell[3] > next_job[3]:
                memory[x + next_job[3]][0] = -1
                memory[x + next_job[3]][3] = cur_cell[3] - next_job[3]
                memory[x] = jobs.popleft()
                return


# Put job in best available fit
# memory - The state of the memory
# jobs - Jobs queue
def best_fit(memory, jobs):
    next_job = jobs[0]
    least_cell = -1
    least_cell_values = []
    for x in range(len(memory)):
        cur_cell = memory[x]
        if cur_cell[0] == -1:
            if cur_cell[3] == next_job[3]:
                memory[x] = jobs.popleft()
                return
            elif cur_cell[3] > next_job[3] and (least_cell == -1 or cur_cell[3] < least_cell_values[3]):
                least_cell = x
                least_cell_values = cur_cell
    if not least_cell == -1:
        memory[least_cell + next_job[3]][0] = -1
        memory[least_cell + next_job[3]][3] = least_cell_values[3] - next_job[3]
        memory[least_cell] = jobs.popleft()
        return


# Put job in worst available fit
# memory - The state of the memory
# jobs - Jobs queue
def worst_fit(memory, jobs):
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
            return
        else:
            memory[biggest_cell + next_job[3]][0] = -1
            memory[biggest_cell + next_job[3]][3] = biggest_cell_values[3] - next_job[3]
            memory[biggest_cell] = jobs.popleft()
            return


# Process the process and clear memory of finished processes
# memory - The state of the memory
# current_job - The ID of the job we are processing currently
# jobs_processed - The count of jobs processed
# avg_time_figures - The table for average timers
# Returns:
#   current_job
#   num_of_occupied (Statistics)
#   num_of_holes (Statistics)
#   total_occupied_size (Statistics)
#   total_holes_size (Statistics)
#   avg_time_figures (Statistics)
def process_memory(memory, current_job, jobs_processed, avg_time_figures):
    lowest_time = [5000, -1, 0]

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
                        avg_time_figures[0] = avg_time_figures[0] + (((cycle - cur_cell[1]) - avg_time_figures[0]) / jobs_processed)
                    cur_cell = [-1, 0, 0, cur_cell[3]]
                else:
                    lowest_time = [cur_cell[1], cur_cell[0], cur_cell[2]]
                cur_cell[2] = cur_cell[2] - 1
                memory[x] = cur_cell
            else:
                if cur_cell[1] < lowest_time[0]:
                    lowest_time = [cur_cell[1], cur_cell[0], cur_cell[2]]
        elif cur_cell[0] < 0:

            # Statistics For Holes
            num_of_holes = num_of_holes + 1
            total_holes_size = total_holes_size + cur_cell[3]

    if not lowest_time[1] == current_job:
        current_job = lowest_time[1]
        if not lowest_time[1] == -1:
            if avg_time_figures[1] == 0.0:
                avg_time_figures[1] = lowest_time[0]
            else:
                avg_time_figures[1] = avg_time_figures[1] + (((cycle - lowest_time[0]) - avg_time_figures[1]) / (jobs_processed + 1))
            if avg_time_figures[2] == 0.0:
                avg_time_figures[2] = lowest_time[2]
            else:
                avg_time_figures[2] = avg_time_figures[2] + ((lowest_time[2] - avg_time_figures[2]) / (jobs_processed + 1))

    return current_job, num_of_occupied, num_of_holes, total_occupied_size, total_holes_size, avg_time_figures


def main(fit_type):

    # Operating System Variables
    memory = []
    memory.append([-1, 0, 0, 175])
    jobs = deque([])
    # cycle = 1
    global cycle
    cycle = 1
    last_job_time = 0
    current_job = 1
    cur_job_id = 1
    jobs_processed = 0

    # Statistics Variables
    avg_time_figures = [0.0, 0.0, 0.0]
    rejected_jobs = 0

    for x in range(174):
        memory.append([0, 0, 0, 0])

    # Clock Cycle Simulation
    while cycle < 5000:
        cycle = cycle + 1

        # Job Creation
        last_job_time, cur_job_id = create_job(jobs, last_job_time, cur_job_id)

        # Job Managment
        rejected_jobs = rejected_jobs + manage_jobs(memory, jobs, fit_type)

        # Keep track of longest waiting process and process current process
        current_job, num_of_occupied, num_of_holes, total_occupied_size, total_holes_size, avg_time_figures = \
            process_memory(memory, current_job, jobs_processed, avg_time_figures)

        # More Statistics Variables

        # Statistic Printing
        if cycle > 1000:
            if cycle%200 == 0:
                avg_occupied_size = 0.0
                if num_of_occupied > 0:
                    avg_occupied_size = float(total_occupied_size) / num_of_occupied
                print 'Ocupied Blocks: ' + str(num_of_occupied) + ' Average Size: ' + str(avg_occupied_size) + ''
            if cycle%300 == 0:
                avg_hole_size = 0.0
                if num_of_holes > 0:
                    avg_hole_size = float(total_holes_size) / num_of_holes
                print 'Free Blocks: ' + str(num_of_occupied) + ' Average Size: ' + str(avg_occupied_size) + ''
            if cycle%500 == 0:
                external_fragmentation = total_holes_size * 10
                print str(external_fragmentation) + 'K Byte Fragmentation'
            if cycle%1000 == 0:
                print 'Reject Jobs at ' + str(cycle) + ': ' + str(rejected_jobs)

    print 'Average Turnaround: ' + str(avg_time_figures[0])
    print 'Average Wait Time: ' + str(avg_time_figures[1])
    print 'Average Processing Time: ' + str(avg_time_figures[2])


print '---------------------FIRST FIT------------------------'
main(0)
print '----------------------BEST FIT------------------------'
main(1)
print '---------------------WORST FIT------------------------'
main(2)
print '------------------------DONE--------------------------'
