import tkinter as tk
from tkinter import ttk
import random
import time
import psutil
import statistics


class Process:
    def __init__(self, pid, burst_time, arrival_time, priority):
        self.pid = pid
        self.burstt = burst_time
        self.arrivalt = arrival_time
        self.priority = priority
        self.completiont = 0
        self.waitingt = 0
        self.turnaroundt = 0
        self.startt = -1
        self.remainingt = burst_time


class NonPreemptivePriorityScheduling:
    def __init__(self, processes):
        self.processes = sorted(processes, key=lambda x: (x.arrivalt, x.priority))
        self.context_switches = 0

    def run(self):
        time_elapsed = 0
        completed = 0
        n = len(self.processes)
        queue = []
        self.cpu_usage = []
        self.memory_usage = []

        self.cpu_usage.append(psutil.cpu_percent(interval=None))
        self.memory_usage.append(psutil.virtual_memory().percent)

        while completed < n:
            for process in self.processes:
                if process.arrivalt <= time_elapsed and process.remainingt > 0:
                    queue.append(process)

            if queue:
                queue.sort(key=lambda x: x.priority)
                process = queue.pop(0)
                if process.startt == -1:
                    process.startt = time_elapsed
                time_elapsed += process.remainingt
                process.remainingt = 0
                process.completiont = time_elapsed
                process.turnaroundt = process.completiont - process.arrivalt
                process.waitingt = process.turnaroundt - process.burstt
                completed += 1
                queue.clear()

                self.cpu_usage.append(psutil.cpu_percent(interval=1))
                self.memory_usage.append(psutil.virtual_memory().percent)

                self.context_switches += 1
            else:
                time_elapsed += 1

    def get_statistics(self):
        avg_cpu_usage = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        avg_memory_usage = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        waiting_times = [p.waitingt for p in self.processes if p.completiont != -1]
        fairness = statistics.variance(waiting_times) if len(waiting_times) > 1 else 0
        overhead = self.context_switches * 0.5
        return {
            "Average CPU Usage (%)": avg_cpu_usage,
            "Average Memory Usage (%)": avg_memory_usage,
            "Fairness (ms)": fairness,
            "Overhead (ms)": overhead
        }


def generate_processes(num_processes, max_bt, max_priority):
    processes = []
    for pid in range(num_processes):
        burstt = random.randint(1, max_bt)
        arrivalt = random.randint(0, 10)
        priority = random.randint(1, max_priority)
        processes.append(Process(pid, burstt, arrivalt, priority))
    return processes


def calculate_averages(processes):
    total_completion_time = sum(p.completiont for p in processes if p.completiont != -1)
    total_turnaround_time = sum(p.turnaroundt for p in processes if p.completiont != -1)
    total_waiting_time = sum(p.waitingt for p in processes if p.completiont != -1)
    total_response_time = sum(p.startt - p.arrivalt for p in processes if p.startt != -1)

    n = len([p for p in processes if p.completiont != -1])  # Only count processes that have completed

    average_ct = total_completion_time / n if n > 0 else 0
    average_tt = total_turnaround_time / n if n > 0 else 0
    average_wt = total_waiting_time / n if n > 0 else 0
    average_rt = total_response_time / n if n > 0 else 0

    return average_ct, average_tt, average_wt, average_rt


def print_results(processes):
    results = " PID |   Priority   |   BT  |   AT  |   WT  |   TT  |   CT  |   RT  \n"               
    results +="-"*90 +"\n"

    for process in processes:
        if process.completiont != -1:
            results += (f"{process.pid:<4} | {process.priority:< 12} | {process.burstt:<5} | {process.arrivalt:<5} | "
                    f"{process.waitingt:<5} | {process.turnaroundt:<5} | "
                    f"{process.completiont:<5} | {process.startt - process.arrivalt:<5}\n")

    avg_ct, avg_tt, avg_wt, avg_rt = calculate_averages(processes)
    results += "\n\nAverage Completion Time: {:.2f}".format(avg_ct)
    results += "\nAverage Turnaround Time: {:.2f}".format(avg_tt)
    results += "\nAverage Waiting Time: {:.2f}".format(avg_wt)
    results += "\nAverage Response Time: {:.2f}".format(avg_rt)

    return results


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Non-Preemptive Priority Scheduling Simulation")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        blue = "#65c5e6"
        bgblue = "#92d8f0"
        self.configure(bg=bgblue)

        tk.Label(self, text="Number of Processes:", bg=bgblue).grid(row=0, column=0)
        self.num_processes = tk.Entry(self, bg=blue)
        self.num_processes.grid(row=0, column=1)

        tk.Label(self, text="Maximum Burst Time:", bg=bgblue).grid(row=1, column=0)
        self.max_burst_time = tk.Entry(self, bg=blue)
        self.max_burst_time.grid(row=1, column=1)

        tk.Label(self, text="Maximum Priority:", bg=bgblue).grid(row=2, column=0)
        self.max_priority = tk.Entry(self, bg=blue)
        self.max_priority.grid(row=2, column=1)

        self.run_button = tk.Button(self, text="Run Simulation", bg=bgblue, command=self.run_simulation)
        self.run_button.grid(row=3, column=0, columnspan=2)
        self.results = tk.Text(self, height=20, width=90)
        self.results.grid(row=4, column=0, columnspan=2)

    def run_simulation(self):
        num_processes = int(self.num_processes.get())
        max_burst_time = int(self.max_burst_time.get())
        max_priority = int(self.max_priority.get())
        processes = generate_processes(num_processes, max_burst_time, max_priority)
        scheduler = NonPreemptivePriorityScheduling(processes)
        scheduler.run()

        results = print_results(processes)
        stats = scheduler.get_statistics()
        results += "\n\nAverage CPU Usage: {:.2f}%".format(stats.get("Average CPU Usage (%)", 0))
        results += "\n\nAverage Memory Usage: {:.2f}%".format(stats.get("Average Memory Usage (%)", 0))
        results += "\nFairness (ms): {:.2f}".format(stats.get("Fairness (ms)", 0))
        results += "\nOverhead (ms): {:.2f}".format(stats.get("Overhead (ms)", 0))
        self.results.delete(1.0, tk.END)
        self.results.insert(tk.END, results)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
