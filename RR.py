import tkinter as tk
from tkinter import ttk
from collections import deque
import random
import time  
import psutil
import statistics

class Process:
    def __init__(self,pid,burst_time,arrival_time):
        
        self.pid = pid
        self.burstt = burst_time 
        self.arrivalt = arrival_time
        self.completiont = 0
        self.waitingt = 0
        self.turnaroundt = 0
        self.startt = -1
        self.remainingt =burst_time
        

class RoundRobin:
    def __init__(self,processes,quantum):
        self.processes = sorted(processes,key=lambda x:x.arrivalt)
        self.quantum = quantum
        self.context_switches = 0
        
    def runRR(self):
        time_elapsed = 0
        queue = deque()
        index = 0
        self.cpu_usage =[]
        self.memory_usage = []
        
        self.cpu_usage.append(psutil.cpu_percent(interval=None))
        self.memory_usage.append(psutil.virtual_memory().percent)
        
        while index < len(self.processes) or queue:
            while index < len(self.processes) and self.processes[index].arrivalt <=time_elapsed:        
                queue.append(self.processes[index])
                index +=1
                
            if queue:
                process = queue.popleft()
                if process.startt == -1:
                    process.startt = time_elapsed
                    
                exect = min(self.quantum,process.remainingt)
                process.remainingt -=exect
                time_elapsed += exect
                
                time.sleep(0.1)
                
                self.cpu_usage.append(psutil.cpu_percent(interval=1))
                self.memory_usage.append(psutil.virtual_memory().percent)

                self.context_switches +=1
                
                if process.remainingt ==0:
                    process.completiont = time_elapsed
                    process.turnaroundt = process.completiont - process.arrivalt
                    process.waitingt = process.turnaroundt - process.burstt
                else:
                    queue.append(process)
                
                while index < len(self.processes) and self.processes[index].arrivalt <= time_elapsed:
                    queue.append(self.processes[index])
                    index += 1
                
                print(f"Time: {time_elapsed}, Context Switches: {self.context_switches}, "
                  f"Process: {process.pid if process else 'None'}, "
                  f"Remaining Time: {process.remainingt if process else 'N/A'}, ")    
            
            else:
                time_elapsed +=1
    
    def get_statistics(self):
        avg_cpu_usage = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        avg_memory_usage = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        waiting_times = [p.waitingt for p in self.processes if p.completiont != -1]
        fairness = statistics.variance(waiting_times) if len(waiting_times) > 1 else 0
        overhead = self.context_switches * 0.5 
        return {"Average CPU Usage (%)" : avg_cpu_usage,
                "Average Memory Usage (%)" : avg_memory_usage,
                "Fairness (ms)" : fairness,
                "Overhead (ms)" : overhead
                }
                
def generate_processes(num_processes,max_bt):
    processes = []
    for pid in range(num_processes):
        burstt = random.randint(1,max_bt)
        arrivalt = random.randint(0,50)
        processes.append(Process(pid,burstt,arrivalt))        
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
    results = "PID | BT | AT | WT | TT | CT | RT\n"               
    results +="-"*50 +"\n"
    
    for process in processes:
        if process.completiont != -1:
            results +=(f"{process.pid:<5} {process.burstt:<4} {process.arrivalt:<5}"
                   f"{process.waitingt:<4} {process.turnaroundt:<4} {process.completiont:<4} {process.startt - process.arrivalt :<4}\n")
    
    avg_ct, avg_tt, avg_wt, avg_rt = calculate_averages(processes)
    results += "\n\nAverage Completion Time: {:.2f}".format(avg_ct)
    results += "\nAverage Turnaround Time: {:.2f}".format(avg_tt)
    results += "\nAverage Waiting Time: {:.2f}".format(avg_wt)
    results += "\nAverage Response Time: {:.2f}".format(avg_rt)
    
    return results
    

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Round Robin Scheduling Simulation")
        self.geometry("800x600")
        self.create_widgets()
    
    def create_widgets(self):
        red = "#ff8080"
        light_red = "#ff9999"
        bgred="#FFE4E1"
        self.configure(bg=bgred)
        
        tk.Label(self, text="Number of Processes:",bg=bgred).grid(row=0, column=0)
        self.num_processes = tk.Entry(self,bg=light_red)
        self.num_processes.grid(row=0, column=1)
        
        tk.Label(self, text="Maximum Burst Time:",bg=bgred).grid(row=1, column=0) 
        self.max_burst_time = tk.Entry(self,bg=light_red)
        self.max_burst_time.grid(row=1, column=1) 
        
        tk.Label(self, text="Quantum Time:",bg=bgred).grid(row=2, column=0)
        self.quantum_time = tk.Entry(self,bg=light_red)
        self.quantum_time.grid(row=2, column=1)
        
        self.run_button = tk.Button(self, text="Run Simulation",bg=red, command=self.run_simulation)
        self.run_button.grid(row=3, column=0, columnspan=2)
        self.results = tk.Text(self, height=20, width=90)
        self.results.grid(row=4, column=0, columnspan=2)
        
        
    def run_simulation(self):
        num_processes = int(self.num_processes.get())
        max_burst_time = int(self.max_burst_time.get())
        quantum_time = int(self.quantum_time.get())
        processes = generate_processes(num_processes, max_burst_time) # Priority not used in RR
        for process in processes:
                 print(f"PID: {process.pid}, Burst Time: {process.burstt}, Arrival Time: {process.arrivalt}, Remaining Time: {process.remainingt}")
        scheduler = RoundRobin(processes, quantum_time)
        scheduler.runRR()
        
        
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
