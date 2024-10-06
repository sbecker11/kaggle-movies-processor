

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

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

def plot_column_distribution(df, col, title=""):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df[col], histnorm='probability density'))
    fig.update_layout(title_text=f'{title} Distribution of column: {col}')
    fig.show()
    
    # allow keyboard entry while figure is displayed
    # plt.ion()

    if input("hit 'c' to continue") == 'c':
        print("Continuing...")
        return