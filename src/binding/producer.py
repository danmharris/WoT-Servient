"""This module represents functionality generic to all binding templates"""

class Producer:
    """Abstract class represending a binding template"""
    def __init__(self):
        """Must inherit constructor, can add extra functionality here if needed"""
    def produce(self):
        """Method to produce WoT compliant things

        Must return a tuple containing
        1. Flask blueprint with endpoints for produced thing
        2. Thing description as a dictionary
        """
