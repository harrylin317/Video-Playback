class Pipeline:
    def __init__(self, stages):
        self.stages = stages
    def run(self, args):
        for stage in self.stages:
            status = stage.process(args)
            if status != 0:
                print("Error encountered in pipeline. Aborting...")
                return status
        return 0 