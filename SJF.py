import tkinter as tk
import random
import time
import psutil
import statistics

class Process:
    def __init__(self, pid, burst_time, arrival_time):
        self.pid = pid
        self.burstt = burst_time
        self.arrivalt = arrival_time
        self.completiont = 0
        self.waitingt = 0
        self.turnaroundt = 0
        self.startt = -1

class ShortestJobFirst:
    def __init__(self, processes):
        self.processes = processes
        self.cpu_usage = []
        self.memory_usage = []
        self.context_switches = 0
        

    def runSJF(self):
        time_elapsed = 0
        processes = sorted(self.processes, key=lambda x: (x.arrivalt, x.burstt))
        while processes:
            # Get the list of processes that have arrived
            arrived_processes = [proc for proc in processes if proc.arrivalt <= time_elapsed]
            if arrived_processes:
                # Select the process with the shortest burst time
                process = arrived_processes[0]
                processes.remove(process)
                # Process starts now
                if process.startt == -1:
                    process.startt = time_elapsed
                # Run the process to completion
                time_elapsed += process.burstt
                # Update process info
                process.completiont = time_elapsed
                process.turnaroundt = process.completiont - process.arrivalt
                process.waitingt = process.turnaroundt - process.burstt
                # Record CPU and memory usage
                self.cpu_usage.append(psutil.cpu_percent(interval=1))
                self.memory_usage.append(psutil.virtual_memory().percent)
                self.context_switches +=1
            else:
                # No process has arrived yet
                time_elapsed += 1

    def get_statistics(self):
        avg_cpu_usage = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        avg_memory_usage = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        waiting_times = [p.waitingt for p in self.processes if p.completiont != -1]
        fairness = statistics.variance(waiting_times) if len(waiting_times) > 1 else 0
        print(f"fainess is : {fairness}")
        overhead = self.context_switches * 0.5 
        
        return {"Average CPU Usage (%)" : avg_cpu_usage,
                "Average Memory Usage (%)" : avg_memory_usage,
                "Fairness (ms)" : fairness,
                "Overhead (ms)" : overhead
                }

def generate_processes(num_processes, max_burst_time):
    return [Process(pid, random.randint(1, max_burst_time), random.randint(0, 50)) for pid in range(num_processes)]

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
    results = " PID |  BT  |   AT  |   WT  |   TT  |   CT  |   RT  \n"               
    results +="-"*70 +"\n"

    for process in processes:
        results += (f"{process.pid:<4} | {process.burstt:<4} | {process.arrivalt:<5} | "
                    f"{process.waitingt:<5} | {process.turnaroundt:<5} | "
                    f"{process.completiont:<5} | {process.startt - process.arrivalt:<5}\n")

    avg_ct, avg_tt, avg_wt, avg_rt = calculate_averages(processes)
    results += "\nAverage Completion Time: {:.2f}\n".format(avg_ct)
    results += "Average Turnaround Time: {:.2f}\n".format(avg_tt)
    results += "Average Waiting Time: {:.2f}\n".format(avg_wt)
    results += "Average Response Time: {:.2f}\n".format(avg_rt)

    return results

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SJF Scheduling Simulation")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        orange = "#f5cba4"
        bgorange="#f7c292"
        self.configure(bg=bgorange)  

        tk.Label(self, text="Number of Processes:", bg=bgorange).grid(row=0, column=0)
        self.num_processes = tk.Entry(self, bg=orange)  # Lighter red
        self.num_processes.grid(row=0, column=1)

        tk.Label(self, text="Maximum Burst Time:",bg=bgorange).grid(row=1, column=0) 
        self.max_burst_time = tk.Entry(self,bg=orange)
        self.max_burst_time.grid(row=1, column=1) 
        
        self.run_button = tk.Button(self, text="Run Simulation",bg=orange, command=self.run_simulation)
        self.run_button.grid(row=3, column=0, columnspan=2)
        self.results = tk.Text(self, height=20, width=90)
        self.results.grid(row=4, column=0, columnspan=2)
        
    def run_simulation(self):
        num_processes = int(self.num_processes.get())
        max_burst_time = int(self.max_burst_time.get())
        processes = generate_processes(num_processes, max_burst_time) 
        scheduler = ShortestJobFirst(processes)
        scheduler.runSJF()
        
        
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