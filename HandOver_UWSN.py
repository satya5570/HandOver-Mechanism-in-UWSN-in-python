import random
import time
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

class UnderwaterNode:
    def __init__(self, node_id, x, y, z, signal_range, initial_energy):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.z = z
        self.signal_range = signal_range
        self.neighbors = set()
        self.visited = False
        self.energy = initial_energy

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)

    def remove_neighbor(self, neighbor):
        self.neighbors.remove(neighbor)

    def is_in_range(self, other_node):
        distance = ((self.x - other_node.x) ** 2 + (self.y - other_node.y) ** 2 + (self.z - other_node.z) ** 2) ** 0.5
        return distance <= self.signal_range

    def calculate_distance(self, other_node):
        distance = ((self.x - other_node.x) ** 2 + (self.y - other_node.y) ** 2 + (self.z - other_node.z) ** 2) ** 0.5
        return distance

    def forward_data(self, data, destination, network, transmission_path):
        if destination == self.node_id:
            print(f"Node {self.node_id}: Data reached destination - '{data}'.")
        else:
            next_hop = self.choose_next_hop(destination, network)
            if next_hop:
                distance = self.calculate_distance(network.nodes[next_hop])
                if distance <= self.signal_range:
                    propagation_time = distance / 1500.0  # Adjust speed of sound in water
                    print(f"Node {self.node_id}: Forwarding data to Node {next_hop}. Distance: {distance:.2f} units.")
                    self.energy -= 5  # Simulating energy consumption
                    time.sleep(propagation_time)
                    transmission_path.append((self.node_id, next_hop, distance))
                    self.visited = True
                    return next_hop
                else:
                    # Enhance signal range until a suitable node is found
                    while True:
                        nearby_nodes = [node_id for node_id, node in network.nodes.items()
                                        if node_id != self.node_id and node_id not in transmission_path and not node.visited
                                        and self.calculate_distance(node) <= self.signal_range * 2]
                        if nearby_nodes:
                            print(f"Node {self.node_id}: No nodes within signal range for handover. Attempting to enhance signal range.")
                            self.signal_range *= 1.5  # Enhance signal range
                            print(f"Node {self.node_id}: Signal range enhanced to {self.signal_range:.2f}.")
                            next_hop = self.choose_next_hop(destination, network)
                            if next_hop:
                                distance = self.calculate_distance(network.nodes[next_hop])
                                if distance <= self.signal_range:
                                    propagation_time = distance / 1500.0  # Adjust speed of sound in water
                                    print(f"Node {self.node_id}: Forwarding data to Node {next_hop}. Distance: {distance:.2f} units.")
                                    self.energy -= 5  # Simulating energy consumption
                                    time.sleep(propagation_time)
                                    transmission_path.append((self.node_id, next_hop, distance))
                                    self.visited = True
                                    return next_hop
                            else:
                                print(f"Node {self.node_id}: Still no nodes within enhanced signal range.")
                        else:
                            print(f"Node {self.node_id}: No nearby nodes found for handover.")
                            break
                    print(f"Node {self.node_id}: Data transfer stopped.")
            else:
                print(f"Node {self.node_id}: No available neighbors. Data transfer stopped.")
                return None

    def send_data(self, next_hop, data, destination, network, transmission_path):
        # Simulate data transmission without acoustic delays
        time.sleep(1)

        # Check if the next_hop is still in the network (it might have moved out of range during the delay)
        if next_hop in network.nodes:
            next_hop.receive_data(data, destination, network, transmission_path)

    def choose_next_hop(self, destination, network):
        reachable_nodes = {neighbor for neighbor in self.neighbors if network.nodes[neighbor].is_in_range(self)}
        reachable_nodes.add(destination)
        reachable_nodes = [node_id for node_id in reachable_nodes if not network.nodes[node_id].visited]
        if not reachable_nodes:
            return None
        return min(reachable_nodes, key=lambda node_id: self.calculate_distance(network.nodes[node_id]))

    def receive_data(self, data, destination, network, transmission_path):
        print(f"Node {self.node_id}: Received data - '{data}'")
        if destination != self.node_id:
            next_hop = self.choose_next_hop(destination, network)
            if next_hop:
                self.send_data(next_hop, data, destination, network, transmission_path)

class UnderwaterNetwork:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id, x, y, z, signal_range, initial_energy):
        if node_id not in self.nodes:
            self.nodes[node_id] = UnderwaterNode(node_id, x, y, z, signal_range, initial_energy)

    def add_edge(self, node1, node2):
        self.nodes[node1].add_neighbor(node2)
        self.nodes[node2].add_neighbor(node1)

    def visualize_network(self, transmission_path, source_node, destination_node):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for node_id, node in self.nodes.items():
            if node_id == source_node:
                color = 'g'  # Source node (green)
            elif node_id == destination_node:
                color = 'r'  # Destination node (red)
            else:
                color = 'b'  # Intermediate nodes (blue)

            ax.scatter(node.x, node.y, node.z, c=color, marker='o', s=15)
            ax.text(node.x, node.y, node.z, f'{node_id} ', fontsize=8)
                                    # ({node.energy})
        for i in range(1, len(transmission_path)):
            start_node, end_node, distance = transmission_path[i]
            start_pos = (self.nodes[start_node].x, self.nodes[start_node].y, self.nodes[start_node].z)
            end_pos = (self.nodes[end_node].x, self.nodes[end_node].y, self.nodes[end_node].z)

            ax.plot3D([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], [start_pos[2], end_pos[2]], 'g-', linewidth=1)

            # Annotate the distance on the plot
            mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2, (start_pos[2] + end_pos[2]) / 2)
            ax.text(mid_pos[0], mid_pos[1], mid_pos[2], f'{distance:.2f}', fontsize=6, color='k')

        plt.show()

def simulate_data_forwarding(network, source_node, destination_node, data):
    transmission_path = [(source_node, source_node, 0)]  # Initial distance is 0
    current_node = source_node
    while current_node != destination_node:
        next_hop = network.nodes[current_node].forward_data(data, destination_node, network, transmission_path)
        if next_hop is None:
            break
        current_node = next_hop
    return transmission_path  # Return the transmission path

def run_simulation(num_nodes, source_node, destination_node):
    network = UnderwaterNetwork()

    # Create nodes and set their coordinates, signal ranges, and initial energy
    for i in range(1, num_nodes + 1):
        network.add_node(i, random.uniform(0, 100), random.uniform(0, 100), random.uniform(0, 100), signal_range=20.0, initial_energy=100.0)

    # Connect nodes to form a simple network
    for i in range(1, num_nodes + 1):
        for j in range(i + 1, num_nodes + 1):
            network.add_edge(i, j)

    print(f"\nRunning simulation for {num_nodes} nodes...")
    start_time = time.time()

    network.add_edge(source_node, destination_node)

    # Simulate data transfer
    data = "Underwater Data"
    transmission_path = simulate_data_forwarding(network, source_node, destination_node, data)

    # Calculate time taken for data transfer
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken for data transfer: {time_taken:.2f} seconds")

    # Print energy level of active nodes
    active_nodes_energy = 0
    active_nodes_count = 0
    for node_id, node in network.nodes.items():
        if node_id != source_node and node_id != destination_node and node.visited:
            active_nodes_energy += node.energy
            active_nodes_count += 1
            print(f"Node {node_id}: Energy level - {node.energy:.2f}")
    if active_nodes_count > 0:
        print(f"Total energy of active nodes: {active_nodes_energy:.2f}")

    # Visualize the network
    network.visualize_network(transmission_path, source_node, destination_node)

    return time_taken, active_nodes_energy

# Create Tkinter window
root = tk.Tk()
root.title("Underwater Network Simulation")

# Title label
title_label = tk.Label(root, text="Underwater Network Simulation", font=("Helvetica", 18), pady=10)
title_label.grid(row=0, column=0, columnspan=2)

# Function to run simulation for phases
def run_phases():
    # Get source and destination nodes from user input
    source = int(source_var.get())
    destination = int(destination_var.get())
    if source <= 0 or source > 150 or destination <= 0 or destination > 150:
        messagebox.showerror("Error", "Please enter valid node numbers (1-150)")
        return

    phase_data = []

    # Run simulation for each phase
    for num_nodes in [150, 250, 500, 750, 1000]:
        time_taken, total_energy_consumed = run_simulation(num_nodes, source, destination)
        phase_data.append((num_nodes, time_taken, total_energy_consumed))

    # Plotting time and energy graphs for each phase
    plt.figure(figsize=(10, 5))

    # Time graph
    plt.subplot(1, 2, 1)
    plt.plot([data[0] for data in phase_data], [data[1] for data in phase_data], marker='o')
    plt.title("Time Consumption")
    plt.xlabel("Number of Nodes")
    plt.ylabel("Time (seconds)")
    plt.grid(True)

    # Energy graph
    plt.subplot(1, 2, 2)
    plt.plot([data[0] for data in phase_data], [data[2] for data in phase_data], marker='o', color='r')
    plt.title("Remaining Energy")
    plt.xlabel("Number of Nodes")
    plt.ylabel("Total Energy Consumed")
    plt.grid(True)

    plt.suptitle("Simulation Results for Different Phases")
    plt.tight_layout()
    plt.show()

# Label and entry for source node
source_label = tk.Label(root, text="Enter source node number:", font=("Helvetica", 12))
source_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

source_var = tk.StringVar()
source_entry = tk.Entry(root, textvariable=source_var, font=("Helvetica", 12), width=10)
source_entry.grid(row=1, column=1, padx=10, pady=5)

# Label and entry for destination node
destination_label = tk.Label(root, text="Enter destination node number:", font=("Helvetica", 12))
destination_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

destination_var = tk.StringVar()
destination_entry = tk.Entry(root, textvariable=destination_var, font=("Helvetica", 12), width=10)
destination_entry.grid(row=2, column=1, padx=10, pady=5)

# Add button to run simulation for phases
simulate_button = tk.Button(root, text="Run Phases", command=run_phases, font=("Helvetica", 14), bg="#4CAF50", fg="white")
simulate_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
