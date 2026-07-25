class PipelineCoordinator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating new PipelineCoordinator instance...")
            cls._instance = super().__new__(cls)
        else:
            print("Using existing PipelineCoordinator instance...")
        return cls._instance

    def __init__(self):
        self.status = "Running"


obj1 = PipelineCoordinator()
obj2 = PipelineCoordinator()

print(obj1 is obj2)
print(obj1.status)
print(obj2.status)