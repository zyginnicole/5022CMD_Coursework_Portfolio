"""
5022CMD Advanced Algorithms - Portfolio
Question 3: Concurrent process (multithreading vs no multithreading)

"""

import threading   # Python's built-in module for creating threads
import time        # used to read the system clock in nanoseconds

# Variable settings
NUMBERS = [35, 38, 40] # the
ROUNDS = 10

# Part 1: Fibonacci function
def fibonacci(n):
    """
    Return the nth Fibonacci number using recursion.

    Big-O (counting primitive operations):
    Each time the function runs, it does a few small steps:
        - check if n is 0 or 1        (1 step)
        - work out n-1 and n-2        (2 steps)
        - add the two answers         (1 step)
        - return the result           (1 step)
    This list is a fixed amount of work every call.

    So each call does a constant amount of work, c, plus two more calls:
          T(n) = T(n-1) + T(n-2) + c        and   T(0) = T(1) = 1
    Thus the number of calls doubles up each time n goes up by 1.
    This is called exponential time, written O(2^n),
    and it is why Fibonacci(40) takes so much longer than Fibonacci(35).
    """

    # Base case when n = 0 or n = 1
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Part 2: Using multithreading
def fib_task(n, position, results, end_times):
    """Work done by only ONE thread.

        n         : which Fibonacci number this thread must calculate
        position  : this thread's own place (0, 1 or 2) in the two lists below
        results   : shared list where the answer is stored
        end_times : shared list where the finishing time is stored

        Each thread writes only to its OWN position in the lists, so two
        threads never write to the same place.
        No race condition and no lock is needed.
        """

    # do the calculation
    results[position] = fibonacci(n)
    # time when the thread finishes
    end_times[position] = time.perf_counter_ns()

def with_threads():
    # run one round using 3 threads, returns time in ns and results
    results = [None] * len(NUMBERS) # room for the 3 answers
    end_times = [None] * len(NUMBERS) # room for 3 finishing times

    #One thread for each customer (no executoon yet)
    threads = []

    for position, n in enumerate(NUMBERS):
        thread = threading.Thread(target=fib_task,
                                  args=(n, position, results, end_times))

        threads.append(thread)

    t1 = time.perf_counter_ns()

    # start all 3 threads
    for t in threads:
        t.start()

    # wait here until every thread has finished
    for t in threads:
        t.join()

    # t2 = end time of the thread the finished LAST
    t2 = max(end_times)

    return t2 - t1, results

# Part 3: Without multithreading
def without_threads():
    # Run one round per number (after another) returns T in ns, results
    results = []

    t1 = time.perf_counter_ns() # record start time
    for n in NUMBERS:
        # each calculation waits for the previous one
        results.append(fibonacci(n))

    t2 = time.perf_counter_ns() # end time

    return t2 - t1, results

# Part 4: Run an experiment for several rounds and shows the results
def run_experiment(title, function_name):
    """Run a function for ROUNDS times
    print every time taken and the average"""

    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

    total = 0
    for r in range(1, ROUNDS + 1):
        time_taken, results = function_name()
        total += time_taken

        print(f"Round {r:>2}: T = {time_taken:>18,}  "
              f"({time_taken / 1_000_000_000:.3f} s)")

    # Summary printed once, after all rounds
    average = total / ROUNDS
    print("-" * 60)
    print(f"Total time: {total:,} ns")
    print(f"Average of T: {average:,.0f} ns ({average / 1_000_000_000:.3f} s)")

    return average

# Main program
if __name__ == "__main__":
    print(f"Calculating Fibonacci{tuple(NUMBERS)} over {ROUNDS} rounds...")

    # One round first, show the answers, make sure they are correct
    _, ans = without_threads()
    for n, value in zip(NUMBERS, ans):
        print(f"Fibonacci {n}: {value:,}")

    # Experiment 1: with multithreading
    avg_threads = run_experiment("EXPERIMENT 1: RUN WITH MULTITHREADING (3 THREADS)",
                                 with_threads)


    # Experiment 2: without multithreading
    avg_normal = run_experiment("EXPERIMENT 2: WITHOUT MULTITHREADING",
                                without_threads)

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON (average time per round)")
    print("=" * 60)
    print(f"With threads    : {avg_threads:>18,.0f} ns")
    print(f"Without threads : {avg_normal:>18,.0f} ns")
    print(f"Without / With  : {avg_normal / avg_threads:.2f}x")
