import threading
import time
import pandas as pd

# Define the message display function
def display_message_every_n_seconds(message, interval, stop_event):
    while not stop_event.is_set():
        print(message)
        time.sleep(interval)

# Define the wrapper function
def run_with_message(func, args=(), kwargs={}, interval_seconds=5, message="Working..."):
    result = [None]
    exception = [None]
    stop_event = threading.Event()

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
        finally:
            stop_event.set()

    thread = threading.Thread(target=target)
    message_thread = threading.Thread(target=display_message_every_n_seconds, args=(message, interval_seconds, stop_event))

    thread.start()
    message_thread.start()

    thread.join()
    message_thread.join()

    if exception[0]:
        raise exception[0]
    return result[0]

def simulated_all_column_values_match(df, col, column_type):
    # Simulate a long-running task
    time.sleep(10)
    return True

def example_usage():
    # Example usage
    df = pd.DataFrame({'values': [1, 2, 'a', 3, 'b', 3, 4, 'c', 4, 4, 5, 'd', 5, 5, 5, None]})
    col = 'values'
    column_type = 'numeric'

    try:
        all_values_match = run_with_message(simulated_all_column_values_match, args=(df, col, column_type), interval_seconds=2, message=f"Checking all values of column: '{col}' for type {column_type}...")
        if all_values_match:
            print(f"All non-null values of column: '{col}' are of type {column_type}")
        else:
            print(f"Some non-null values of column: '{col}' are not of type {column_type}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
if __name__ == "__main__":
    example_usage()