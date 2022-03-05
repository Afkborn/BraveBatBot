
class Process:
    def __init__(self,handle_count,name,priority,process_id,thread_count,working_set_size):
        self.handle_count = handle_count
        self.name = name
        self.priority = priority
        self.process_id = process_id
        self.thread_count = thread_count
        self.working_set_size = working_set_size
    
    def __str__(self):
        return f"{self.name} {self.process_id} {self.priority} {self.handle_count} {self.thread_count} {self.working_set_size}"
