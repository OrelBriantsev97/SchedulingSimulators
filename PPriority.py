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

class PreemptivePriority:
    def __init__(self, processes):
        self.processes = processes
        self.context_switches = 0
        print("im here1")

    

    def runPP(self):
        time_elapsed = 0
        ready_queue = []
        index = 0
        self.cpu_usage = []
        self.memory_usage = []
        counter = 0
        current_process = None
        n = len(self.processes)
        completed = 0
        previous_process = None

        self.cpu_usage.append(psutil.cpu_percent(interval=None))
        self.memory_usage.append(psutil.virtual_memory().percent)
    
        while completed <n or ready_queue:
        # Add new processes to the ready queue when they arrive
            while index < n and self.processes[index].arrivalt <= time_elapsed:
                ready_queue.append(self.processes[index])
                index += 1

        # If the ready queue is not empty, choose the process with the highest priority (smallest value)
            if ready_queue:
                ready_queue.sort(key=lambda x: (x.arrivalt,x.priority))
                new_process = ready_queue[0]  # Process with the highest priority gets the CPU time

                if current_process is None or new_process.priority < current_process.priority:
                    if  current_process and new_process != current_process and current_process.remainingt > 0:
                        self.context_switches += 1  # Increment context switch when a new process takes over
                    current_process = new_process 
                    
                if current_process.startt == -1:
                    current_process.startt = time_elapsed
                    
                
                current_process.remainingt -= 1
                time_elapsed += 1
                
                time.sleep(0.1)

                self.cpu_usage.append(psutil.cpu_percent(interval=0.1))
                self.memory_usage.append(psutil.virtual_memory().percent)

            # If the current process has completed its burst time, remove it from the ready queue
                if current_process.remainingt == 0:
                    current_process.completiont = time_elapsed
                    current_process.turnaroundt = current_process.completiont - current_process.arrivalt
                    current_process.waitingt = current_process.turnaroundt - current_process.burstt
                    if current_process in ready_queue:
                        ready_queue.remove(current_process)
                        current_process = None
                    completed +=1
            else:
            # If no process is in the ready queue, just advance time
                time_elapsed += 1
                
            remaining_processes = len([p for p in self.processes if p.remainingt > 0])
             # Increment context switch count only if the process was changed in the current time unit
            print(f"Time: {time_elapsed}, Context Switches: {self.context_switches}, "
                  f"Process: {current_process.pid if current_process else 'None'}, "
                  f"Remaining Time: {current_process.remainingt if current_process else 'N/A'}, "
                  f"Remaining Processes: {remaining_processes}")



    def get_statistics(self):
        print("hii girl")
        avg_cpu_usage = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        avg_memory_usage = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        waiting_times = [p.waitingt for p in self.processes if p.completiont != -1]
        fairness = statistics.variance(waiting_times) if len(waiting_times) > 1 else 0
        overhead = self.context_switches * 0.5
        return {
            "Average CPU Usage (%)": avg_cpu_usage,
            "Average Memory Usage (%)": avg_memory_usage,
            "Fairness (ms)": fairness,
            "Overhead (ms)": overhead,
        }
        
        
def generate_processes(num_processes, max_burst_time,max_priority):
    processes = []
    for pid in range(num_processes):
        burstt = random.randint(1, max_burst_time)
        arrivalt = random.randint(0, 10)
        priority = random.randint(1, max_priority)
        processes.append(Process(pid, burstt, arrivalt, priority))
        
    return processes

def calculate_averages(processes):
    total_completion_time = sum(p.completiont for p in processes)
    total_turnaround_time = sum(p.turnaroundt for p in processes)
    total_waiting_time = sum(p.waitingt for p in processes)
    total_response_time = sum(p.startt - p.arrivalt for p in processes)

    n = len(processes)
    average_ct = total_completion_time / n
    average_tt = total_turnaround_time / n
    average_wt = total_waiting_time / n
    average_rt = total_response_time / n

    return average_ct, average_tt, average_wt, average_rt

def print_results(processes):
    results = " PID |   Priority   |   BT  |   AT  |   WT  |   TT  |   CT  |   RT  \n"               
    results +="-"*90 +"\n"

    for process in processes:
        results += (f"{process.pid:<4} | {process.priority:< 12} | {process.burstt:<5} | {process.arrivalt:<5} | "
                    f"{round(process.waitingt,4):<5} | {round(process.turnaroundt,4):<5} | "
                    f"{round(process.completiont,4):<5} | {round(process.startt - process.arrivalt,4):<5}\n")

    avg_ct, avg_tt, avg_wt, avg_rt = calculate_averages(processes)
    results += "\nAverage Completion Time: {:.2f}\n".format(avg_ct)
    results += "Average Turnaround Time: {:.2f}\n".format(avg_tt)
    results += "Average Waiting Time: {:.2f}\n".format(avg_wt)
    results += "Average Response Time: {:.2f}\n".format(avg_rt)

    return results

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Preemptive Priority Scheduling Simulation")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        green = "#63ab67"
        bggreen="#84ba87"
        self.configure(bg=bggreen)  

        tk.Label(self, text="Number of Processes:", bg=bggreen).grid(row=0, column=0)
        self.num_processes = tk.Entry(self, bg=green)  # Lighter red
        self.num_processes.grid(row=0, column=1)

        tk.Label(self, text="Maximum Burst Time:",bg=bggreen).grid(row=1, column=0) 
        self.max_burst_time = tk.Entry(self,bg=green)
        self.max_burst_time.grid(row=1, column=1) 
        
        tk.Label(self, text="Maximum Priority:", bg=bggreen).grid(row=2, column=0)
        self.max_priority = tk.Entry(self, bg=green)
        self.max_priority.grid(row=2, column=1)
        
        self.run_button = tk.Button(self, text="Run Simulation",bg=bggreen, command=self.run_simulation)
        self.run_button.grid(row=3, column=0, columnspan=2)
        self.results = tk.Text(self, height=20, width=90)
        self.results.grid(row=4, column=0, columnspan=2)
        
    def run_simulation(self):
        num_processes = int(self.num_processes.get())
        max_burst_time = int(self.max_burst_time.get())
        max_priority = int(self.max_priority.get())
        processes = generate_processes(num_processes, max_burst_time,max_priority)
        for process in processes:
            print(f"PID: {process.pid}, Burst Time: {process.burstt}, Arrival Time: {process.arrivalt}, Priority: {process.priority}, Remaining Time: {process.remainingt}")
        scheduler = PreemptivePriority(processes)
        scheduler.runPP()
        
        
        results = print_results(processes)
        stats = scheduler.get_statistics()
        print(f"stats are : {stats}")
        results += "\n\nAverage CPU Usage: {:.2f}%".format(stats.get("Average CPU Usage (%)",0))
        results += "\n\nAverage Memory Usage: {:.2f}%".format(stats.get("Average Memory Usage (%)",0))
        results += "\nFairness (ms) {:.2f}".format(stats.get("Fairness (ms)", 0))
        results += "\nOverhead (ms): {:.2f}".format(stats.get("Overhead (ms)", 0))
        self.results.delete(1.0, tk.END)
        self.results.insert(tk.END, results) 
        
if __name__ == "__main__":
    app = Application()
    app.mainloop() 


