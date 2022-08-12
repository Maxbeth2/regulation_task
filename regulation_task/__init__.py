from gym.envs.registration import register


register(id='RegulationTask-v0',
        entry_point='regulation_task.envs:RegulationTask')