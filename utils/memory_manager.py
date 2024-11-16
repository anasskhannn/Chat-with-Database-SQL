class MemoryManager:
    def __init__(self):
        self.memory = {}

    def get_memory(self, query):
        return self.memory.get(query)

    def store_memory(self, query, result):
        self.memory[query] = result

# Initialize memory manager
memory_manager = MemoryManager()
