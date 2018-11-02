

class Const(object):
    
    INFERENCE_TYPES = ['none', 'particleFilter', 'exactInference']
    TITLE = "Driverless Car Simulator"
    SONAR_STD = 20.0
    
    TRAIN_ITERATIONS = 500
    TRAIN_MAX_AGENTS = 3
    TRAIN_PER_AGENT_COUNT = 4
    
    LAYOUT_DIR = 'layouts'
    
    BLOCK_TILE_SIZE = 30
    BELIEF_TILE_SIZE = 30
    REPORT_ITER = 100
    
    UI_HEARTBEATS_PER_SECOND = 20
    SECONDS_PER_UI_HEARTBEAT = 1.0 / UI_HEARTBEATS_PER_SECOND
    
    SIM_SPEED = 'slow'
    
    HEARTBEAT_DICT = {
        'veryFast': 9,
        'fast':7,
        'slow':5,
        'verySlow':3,
    }

    HEARTBEATS_PER_SECOND = HEARTBEAT_DICT[SIM_SPEED]
    SECONDS_PER_HEARTBEAT = 1.0 / HEARTBEATS_PER_SECOND
    
    EPSILON = 0.0001

    WORLD = 'lombard'
    

    
    
