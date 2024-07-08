class ReservationStation:
    def __init__(self):
        self.busy = False
        self.operation = None
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.result = None


class FunctionalUnit:
    def __init__(self):
        self.busy = False
        self.remaining_cycles = 0
        self.instruction = None


class TomasuloCPU:
    def __init__(self, num_rs, num_fu):
        self.reservation_stations = [ReservationStation() for _ in range(num_rs)]
        self.functional_units = [FunctionalUnit() for _ in range(num_fu)]
        self.register_file = {}
        self.instructions = []

    def issue(self, instruction, cycle):
        for i, rs in enumerate(self.reservation_stations):
            if not rs.busy:
                rs.busy = True
                rs.operation = instruction["op"]
                rs.Vj = self.get_value(instruction["src1"])
                rs.Vk = self.get_value(instruction["src2"])
                rs.Qj = self.get_rs_or_register(instruction["src1"])
                rs.Qk = self.get_rs_or_register(instruction["src2"])
                instruction["rs_index"] = i
                break

    def execute(self, cycle):
        for rs in self.reservation_stations:
            if rs.busy and rs.Qj is None and rs.Qk is None:
                for fu in self.functional_units:
                    if not fu.busy and fu.remaining_cycles == 0:
                        fu.busy = True
                        fu.remaining_cycles = self.get_execution_time(rs.operation)
                        fu.instruction = rs
                        rs.result = None
                        rs.busy = False
                        break

    def write_result(self, cycle):
        for fu in self.functional_units:
            if fu.busy and fu.remaining_cycles == 1:
                rs = fu.instruction
                rs.result = self.execute_operation(rs.operation, rs.Vj, rs.Vk)
                fu.instruction = None
                fu.busy = False
                fu.remaining_cycles = 0
                self.update_registers(rs)

    def get_value(self, operand):
        if operand.isdigit():
            return int(operand)
        elif operand in self.register_file:
            return self.register_file[operand]
        else:
            return None

    def get_rs_or_register(self, operand):
        if operand.isdigit():
            return None
        elif operand in self.register_file:
            return self.register_file[operand]
        else:
            return operand

    def update_registers(self, rs):
        for i, station in enumerate(self.reservation_stations):
            if station.Qj == rs.operation:
                station.Vj = rs.result
                station.Qj = None
            if station.Qk == rs.operation:
                station.Vk = rs.result
                station.Qk = None

    def execute_operation(self, operation, Vj, Vk):
        if operation == 'ADD':
            return Vj + Vk
        elif operation == 'SUB':
            return Vj - Vk
        elif operation == 'MUL':
            return Vj * Vk
        elif operation == 'DIV':
            return Vj / Vk

    def get_execution_time(self, operation):
        return 1

    def run(self):
        cycle = 0
        instruction_index = 0
        while True:
            if instruction_index < len(self.instructions):
                self.issue(self.instructions[instruction_index], cycle)
                instruction_index += 1

            self.execute(cycle)
            self.write_result(cycle)

            if instruction_index >= len(self.instructions) and all(not fu.busy for fu in self.functional_units):
                break

            cycle += 1


cpu = TomasuloCPU(num_rs=3, num_fu=2)
cpu.instructions = [
    {"op": "ADD", "src1": "R1", "src2": "R2"},
    {"op": "MUL", "src1": "R3", "src2": "R4"},
    {"op": "SUB", "src1": "R5", "src2": "R6"},
]
cpu.register_file = {"R1": 10, "R2": 20, "R3": 30, "R4": 40, "R5": 50, "R6": 60}
cpu.run()
