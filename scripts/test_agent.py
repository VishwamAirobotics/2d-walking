import tensorflow as tf
from tf_agents.environments import tf_py_environment
from tf_agents.policies import py_tf_eager_policy
from tf_agents.trajectories import time_step as ts
import numpy as np
import os
import sys

# Add the project's root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment import BirdRobotEnvironment
from config.config import POLICY_DIR

# Print the current working directory and Python path for debugging
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Print the TensorFlow Agents library version for debugging
import tf_agents
print("TF-Agents version:", tf_agents.__version__)

# Create the environment
eval_py_env = BirdRobotEnvironment()
eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)

# Load the trained policy
policy_dir = POLICY_DIR
if not os.path.exists(policy_dir):
    raise FileNotFoundError(f"Policy directory '{policy_dir}' does not exist. Please ensure the model is trained and saved correctly.")

try:
    # Load the saved policy using tf.saved_model.load
    saved_policy = tf.saved_model.load(policy_dir)
    # Debugging: Print the contents of the policy directory and inspect the loaded policy object
    print(f"Contents of policy directory '{policy_dir}': {os.listdir(policy_dir)}")
    print(f"Loaded policy object: {saved_policy}")
    print(f"Attributes of loaded policy object: {dir(saved_policy)}")
    # Check if the saved policy has the 'action' method
    if 'action' not in saved_policy.signatures:
        raise AttributeError("Loaded policy object does not have an 'action' method.")
    # Debugging: Print the signatures of the loaded policy
    print(f"Signatures of loaded policy: {saved_policy.signatures}")
    # Debugging: Print the structure of the 'action' method signature
    if 'action' in saved_policy.signatures:
        action_signature = saved_policy.signatures['action']
        print(f"'action' method signature: {action_signature}")
        print(f"'action' method input signature: {action_signature.input_signature}")
        print(f"'action' method output signature: {action_signature.output_shapes}")
    # Create a policy object using the loaded policy's 'action' signature
    policy = py_tf_eager_policy.SavedModelPyTFEagerPolicy(saved_policy, time_step_spec=eval_env.time_step_spec())
except Exception as e:
    raise RuntimeError(f"Error loading policy from '{policy_dir}': {e}")

# Print TensorFlow version for debugging
print("TensorFlow version:", tf.__version__)

# Run a few episodes and print the results
num_episodes = 10
for _ in range(num_episodes):
    time_step = eval_env.reset()
    episode_return = 0.0

    while not time_step.is_last():
        try:
            action_step = policy.action(time_step)
            time_step = eval_env.step(action_step.action)
            episode_return += time_step.reward
        except AttributeError as e:
            print(f"AttributeError during policy execution: {e}")
            print(f"Attributes of policy object: {dir(policy)}")
            raise

    print('Episode return: {}'.format(episode_return))
