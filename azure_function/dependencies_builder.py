from opentelemetry import trace
from ambient_context import AmbientContext

class DependenciesBuilder:
    def __init__(self):
        self.tracer: trace.Tracer = trace.get_tracer(__name__)
        self.ambient_context = AmbientContext()
