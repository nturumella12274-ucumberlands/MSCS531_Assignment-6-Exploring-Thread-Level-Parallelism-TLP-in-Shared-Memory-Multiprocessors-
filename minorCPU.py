import sys
import os

# Create the system for X86 architecture
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Custom Minor CPU Class inheriting from BaseMinorCPU
class CustomX86MinorCPU(BaseMinorCPU, X86CPU):
    mmu = X86MMU()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.numThreads = 1  # Each core has a single thread by default

# Simple CPU and Memory Configuration
system.mem_mode = 'timing'  # Timing mode for memory
system.mem_ranges = [AddrRange('8192MB')]  # Memory range for the system

# Number of CPU cores
num_cores = 4  # Adjust the number of cores as required
system.cpu = [CustomX86MinorCPU() for _ in range(num_cores)]  # Multi-core setup
system.membus = SystemXBar()  # Memory bus to connect components

# Memory Controller (DDR3 RAM)
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# L1 Cache Configuration (Instruction Cache and Data Cache)
class L1Cache(Cache):
    assoc = 4
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L1ICache(L1Cache):
    size = '64kB'

class L1DCache(L1Cache):
    size = '128kB'

# Set up the L1 Caches for each CPU core
for cpu in system.cpu:
    cpu.icache = L1ICache()
    cpu.dcache = L1DCache()

    # Connect the CPU caches to the CPU
    cpu.icache.cpu_side = cpu.icache_port
    cpu.dcache.cpu_side = cpu.dcache_port
    cpu.icache.mem_side = system.membus.cpu_side_ports
    cpu.dcache.mem_side = system.membus.cpu_side_ports

    # Configure Interrupt Controllers for each CPU core
    cpu.createInterruptController()
    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect the system port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Taking input from the command line for binary file
if '-c' not in sys.argv:
    print("Error: Please specify a binary file with the -c flag.")
    sys.exit(1)

binary = sys.argv[sys.argv.index('-c') + 1]

# Check if the binary exists
if not os.path.isfile(binary):
    print(f"Error: The binary '{binary}' does not exist.")
    sys.exit(1)

# Create processes for the binary workload for each CPU core
process = Process()
process.cmd = [binary]  # Command to run the binary
for cpu in system.cpu:
    cpu.workload = process  # Assign the same workload to all cores
    cpu.createThreads()  # Create CPU threads

# Initialize the workload
system.workload = SEWorkload.init_compatible(binary)

# Simulation Configuration
root = Root(full_system=False, system=system)
m5.instantiate()
print("Beginning of the Simulation!!!!")
exit_event = m5.simulate()
print(f'Exiting @ tick {m5.curTick()} because {exit_event.getCause()}')
