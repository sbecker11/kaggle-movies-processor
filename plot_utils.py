from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from scipy.stats import norm as scipy_norm
import pandas as pd
import numpy as np
from column_types import get_numeric_columns, get_column_type_extractor
from sklearn.preprocessing import StandardScaler
from stat_utils import find_non_numeric_values, find_integer_values, find_float_values


# Show a matrix of histograms for pairs of numeric columns
def show_scatter_and_density(df):
    numeric_df = df.select_dtypes(include=[np.number])
    numeric_cols = numeric_df.columns
    num_cols = len(numeric_cols)

    # Create a grid layout
    fig = make_subplots(rows=num_cols, cols=num_cols, 
                        subplot_titles=[
                            f'{x} vs {y}' for x in numeric_cols for y in numeric_cols],
                        shared_xaxes=True, shared_yaxes=True)

    for i, col1 in enumerate(numeric_cols):
        for j, col2 in enumerate(numeric_cols):
            if i == j:
                # Add density plot on the diagonal
                fig.add_trace(go.Histogram(
                    x=numeric_df[col1], nbinsx=20, histnorm='probability density'), row=i + 1, col=j + 1)
            else:
                # Add scatter plot on the off-diagonal
                fig.add_trace(go.Scatter(
                    x=numeric_df[col2], y=numeric_df[col1], mode='markers'), row=i + 1, col=j + 1)

    fig.update_layout(height=800, width=800,
                      title_text="Scatter Plots and Density Plots")
    fig.show()
    
    # allow keyboard entry while figure is displayed
    # plt.ion()
    
    choice = input("select 'q' to quit")
    if choice == 'q':
        print("Quitting...")
        return

# column's dtype may have been changed to object type for display
# so set the column's dtype to match the type of its values
# which are expected to be all integers or all floats
# does not handle other numeric dtypes, e.g. int16, float32 etc.
# does not first check to see if column's dtype is already int64 or float64
def set_numeric_column_dtype(df, col):
    num_non_numeric_values = len(find_non_numeric_values(df, col))
    if num_non_numeric_values > 0:
        print(f"WARNING: set_numeric_column_dtype skipping column '{col}' has {num_non_numeric_values} non-numeric values.")
        return df
    num_rows = len(df)
    num_integer_values = len(find_integer_values(df, col))
    num_float_values = len(find_float_values(df, col))
    
    # if the column has mixed types, raise an error
    if num_integer_values == num_rows:
        df[col] = df[col].astype('int64')
    elif num_float_values == num_rows:
        df[col] = df[col].astype('float64')
    else:
        raise ValueError(f"plot_column_distribution - column '{col}' has {num_integer_values} integer values and {num_float_values} float values.")
    
    return df


def plot_column_distribution(df, col, title="", mean=None, stddev=None, scale_factor=1):
    
    num_non_numeric_values = len(find_non_numeric_values(df, col))
    if num_non_numeric_values > 0:
        print(f"plot_column_distribution skipping column '{col}' has {num_non_numeric_values} non-numeric values.")
        return
        
    df = set_numeric_column_dtype(df, col)
    
    if mean is None:
        mean = df[col].mean()
    if stddev is None:
        stddev = df[col].std()

    # Create histogram using plotly.express
    fig = px.histogram(df, x=col, histnorm='probability density', nbins=30, title=f'{title} Distribution of column: {col}')
    
    # Calculate PDF
    x = np.linspace(df[col].min(), df[col].max(), 1000)
    pdf = scipy_norm.pdf(x, mean, stddev) * scale_factor
    
    # Add PDF curve using plotly.graph_objects
    pdf_trace = go.Scatter(x=x, y=pdf, mode='lines', name='PDF')
    fig.add_trace(pdf_trace)
    
    # Update layout
    fig.update_layout(title_text=f'{title} Distribution of column: {col}')
    
    plt.ion()
    if input("hit any key to continue: "):
        print("Continuing...")
        plt.ioff()
        plt.close()
        return

    # Show plot and wait for user to close it
    plt.show(block=True)

# def add_close_plot_on_click_area(plt):
#     dummy_fig, dummy_ax = plt.subplots()
#     dummy_fig.canvas.manager.set_window_title('Click to close this window')
#     plt.text(0.5, 0.1, 'Click here to close', horizontalalignment='center', verticalalignment='center')
    
#     def on_click(event):
#         # Check if the click is within the bottom-most line area
#         if event.y < 50:  # Adjust this value as needed
#             plt.close(dummy_fig)
    
#     dummy_fig.canvas.mpl_connect('button_press_event', on_click)
#     plt.show()

    
def create_random_distribution(mean, stddev, size):
    return np.random.normal(mean, stddev, size)

def add_noise_to_distribution(distribution, noise_mean=0, noise_stddev=1, noise_scale=0.1):
    noise = noise_scale * np.random.normal(noise_mean, noise_stddev, len(distribution))
    noisy_distribution = distribution + noise
    return noisy_distribution

def autoscale_numeric_column(df, col, verbose=False):
    # Autoscale a numeric column in a DataFrame
    # using the StandardScaler from scikit-learn
    
    # Get the column type extractor
    column_type_extractor = get_column_type_extractor(col)
    
    # Create a column type matcher which retuns a valid value or None
    def column_type_matcher(x):
        return column_type_extractor(x) is not None
    
    # Create a mask for valid values
    value_mask = df[col].dropna().apply(lambda x: column_type_matcher(x))
    
    # Extract valid values
    valid_values = df[col].dropna()[value_mask]
    
    # Apply StandardScaler to valid values
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(valid_values.values.reshape(-1, 1))
    
    # Reinsert scaled values back into the DataFrame
    df.loc[valid_values.index, col] = scaled_values
    
    if verbose:
        print(f"Column '{col}' has been autoscaled.")
    return df


show_synthetic_data = False
show_real_data = True

if __name__ == '__main__':
    if show_synthetic_data:
        normal_values = create_random_distribution(0, 1, 1000)
        noisy_normal_values = add_noise_to_distribution(normal_values, noise_mean=0, noise_stddev=0.1)
        df = pd.DataFrame({'normal_values': normal_values, 'noisy_normal_values': noisy_normal_values})
        plot_column_distribution(df, 'normal_values', title='Synthetic Data', mean=0, stddev=1, scale_factor=1)
        plot_column_distribution(df, 'noisy_normal_values', title='Synthetic Data with Noise', mean=0, stddev=1, scale_factor=1)

    if show_real_data:
        # # real movies data example
        df = pd.read_csv("movies.csv")
        
        numeric_cols = get_numeric_columns(df)
        for col in numeric_cols:
            if input(f"Want to prepare column {col} for scaling? y/n:") != 'n':
                df = autoscale_numeric_column(df, col, verbose=True)
                
            plot_column_distribution(df, col, title='Real Movies Data')
            if input("hit 'q' to quit: ") == 'q':
                break