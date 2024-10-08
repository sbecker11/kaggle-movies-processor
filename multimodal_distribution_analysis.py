import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import KernelDensity
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth, DBSCAN

# from statsmodels.nonparametric.smoothers_lowess import lowess 
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import BayesianGaussianMixture
from sklearn.ensemble import IsolationForest
from minisom import MiniSom

def plot_distribution(ax, data, title):
    """Helper function to plot the distribution of data."""
    ax.hist(data, bins=50, density=True, alpha=0.7, label='Data Distribution')
    ax.set_title(title)
    ax.set_xlabel('Value')
    ax.set_ylabel('Density')

def gmm_analysis(data, ax, n_components=3):
    print("Analyzing data using Gaussian Mixture Model.")
    gmm = GaussianMixture(n_components=n_components)
    gmm.fit(data.reshape(-1, 1))
    x = np.linspace(data.min(), data.max(), 1000).reshape(-1, 1)
    logprob = gmm.score_samples(x)
    responsibilities = gmm.predict_proba(x)
    
    plot_distribution(ax, data, 'Gaussian Mixture Model')
    ax.plot(x, np.exp(logprob), 'r-', label='GMM')
    for i in range(n_components):
        ax.plot(x, responsibilities[:, i] * gmm.weights_[i] * np.exp(logprob),
                '--', label=f'Component {i+1}')
    ax.legend()

analysis_function_1 = gmm_analysis

def kde_analysis(data, ax):
    print("Analyzing data using Kernel Density Estimation.")
    kde = KernelDensity(bandwidth=0.5, kernel='gaussian')
    kde.fit(data[:, None])
    x = np.linspace(data.min(), data.max(), 1000)[:, None]
    log_dens = kde.score_samples(x)
    
    plot_distribution(ax, data, 'Kernel Density Estimation')
    ax.plot(x, np.exp(log_dens), 'r-', label='KDE')
    ax.legend()

analysis_function_2 = kde_analysis

def histogram_analysis(data, ax):
    print("Analyzing data using histogram analysis with peak detection.")
    counts, bins, _ = ax.hist(data, bins=50, density=True, alpha=0.7)
    ax.set_title('Histogram Analysis')
    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    
    peak_indices, _ = find_peaks(counts)
    for peak in peak_indices:
        ax.axvline(bins[peak], color='r', linestyle='--')
        ax.text(bins[peak], counts[peak], f'Peak: {bins[peak]:.2f}', 
                rotation=90, verticalalignment='bottom')

analysis_function_3 = histogram_analysis

def mode_finding(data, ax):
    print("Analyzing data using mode-finding algorithm based on KDE.")
    kde = gaussian_kde(data)
    x = np.linspace(data.min(), data.max(), 1000)
    y = kde(x)
    
    peak_indices, _ = find_peaks(y)
    modes = x[peak_indices]
    
    plot_distribution(ax, data, 'Mode-finding Algorithm')
    ax.plot(x, y, 'r-', label='KDE')
    for mode in modes:
        ax.axvline(mode, color='g', linestyle='--')
        ax.text(mode, kde(mode), f'Mode: {mode:.2f}', 
                rotation=90, verticalalignment='bottom')
    ax.legend()

analysis_function_4 = mode_finding

def em_algorithm(data, ax, n_components=3):
    print("Analyzing data using Expectation-Maximization algorithm (via GMM).")
    gmm = GaussianMixture(n_components=n_components, n_init=5)
    gmm.fit(data.reshape(-1, 1))
    x = np.linspace(data.min(), data.max(), 1000).reshape(-1, 1)
    logprob = gmm.score_samples(x)
    
    plot_distribution(ax, data, 'Expectation-Maximization Algorithm (GMM)')
    ax.plot(x, np.exp(logprob), 'r-', label='EM (GMM)')
    for i, (mean, covar) in enumerate(zip(gmm.means_, gmm.covariances_)):
        ax.axvline(mean[0], color='g', linestyle='--')
        ax.text(mean[0], np.exp(logprob.max()), f'μ{i+1}: {mean[0]:.2f}\nσ{i+1}: {np.sqrt(covar[0][0]):.2f}', 
                rotation=90, verticalalignment='top')
    ax.legend()

analysis_function_5 = em_algorithm

def finite_mixture_model(data, ax, n_components=3):
    print("Analyzing data using Finite Mixture Model (using GMM as an example).")
    gmm = GaussianMixture(n_components=n_components, covariance_type='full')
    gmm.fit(data.reshape(-1, 1))
    x = np.linspace(data.min(), data.max(), 1000).reshape(-1, 1)
    logprob = gmm.score_samples(x)
    
    plot_distribution(ax, data, 'Finite Mixture Model')
    ax.plot(x, np.exp(logprob), 'r-', label='FMM')
    ax.legend()

analysis_function_6 = finite_mixture_model

def non_parametric_mixture(data, ax):
    print("Analyzing data using Non-parametric Mixture Model (using KDE).")
    kde = gaussian_kde(data)
    x = np.linspace(data.min(), data.max(), 1000)
    y = kde(x)
    
    plot_distribution(ax, data, 'Non-parametric Mixture Model')
    ax.plot(x, y, 'r-', label='NPM')
    ax.legend()

analysis_function_7 = non_parametric_mixture

def mean_shift_clustering(data, ax):
    print("Analyzing data using Mean Shift Clustering.")
    bandwidth = estimate_bandwidth(data.reshape(-1, 1), quantile=0.2)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(data.reshape(-1, 1))
    
    plot_distribution(ax, data, 'Mean Shift Clustering')
    for center in ms.cluster_centers_:
        ax.axvline(center[0], color='r', linestyle='--')
        ax.text(center[0], ax.get_ylim()[1], f'Center: {center[0]:.2f}', 
                rotation=90, verticalalignment='top')

analysis_function_8 = mean_shift_clustering

def kmeans_clustering(data, ax, n_clusters=3):
    print("Analyzing data using K-Means Clustering.")
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(data.reshape(-1, 1))
    centers = kmeans.cluster_centers_
    
    plot_distribution(ax, data, 'K-Means Clustering')
    for center in centers:
        ax.axvline(center[0], color='r', linestyle='--')
        ax.text(center[0], ax.get_ylim()[1], f'Center: {center[0]:.2f}', 
                rotation=90, verticalalignment='top')

analysis_function_9 = kmeans_clustering

def dbscan_clustering(data, ax):
    print("Analyzing data using DBSCAN clustering.")
    
    # Reshape data
    data = data.reshape(-1, 1)
    
    # Perform DBSCAN clustering
    db = DBSCAN(eps=0.5, min_samples=5).fit(data)
    labels = db.labels_
    
    # Plot the results
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    
    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)
        
        xy = data[class_member_mask]
        ax.plot(xy[:, 0], np.zeros_like(xy[:, 0]) + 0.01, 'o', markerfacecolor=tuple(col),
                markeredgecolor='k', markersize=6, label=f'Cluster {k}')
    
    plot_distribution(ax, data, 'DBSCAN Clustering')
    
    # Set y-axis limits to match other plots
    ax.set_ylim(0, 0.5 / 3.25)
    ax.legend()

analysis_function_10 = dbscan_clustering

def agglomerative_clustering(data, ax, n_clusters=3):
    print("Analyzing data using Agglomerative Clustering.")
    agglo = AgglomerativeClustering(n_clusters=n_clusters)
    labels = agglo.fit_predict(data.reshape(-1, 1))
    
    plot_distribution(ax, data, 'Agglomerative Clustering')
    unique_labels = set(labels)
    for label in unique_labels:
        color = plt.cm.Spectral(float(label) / len(unique_labels))
        label_name = f'Cluster {label}'
        ax.hist(data[labels == label], bins=50, density=True, alpha=0.7, color=color, label=label_name)
    ax.legend()

analysis_function_11 = agglomerative_clustering

# def spectral_clustering(data, ax, n_clusters=3):
#     print("Analyzing data using Spectral Clustering.")
#     spectral = SpectralClustering(n_clusters=n_clusters, affinity='nearest_neighbors')
#     labels = spectral.fit_predict(data.reshape(-1, 1))
    
#     plot_distribution(ax, data, 'Spectral Clustering')
#     unique_labels = set(labels)
#     for label in unique_labels:
#         color = plt.cm.Spectral(float(label) / len(unique_labels))
#         label_name = f'Cluster {label}'
#         ax.hist(data[labels == label], bins=50, density=True, alpha=0.7, color=color, label=label_name)
#     ax.legend()

def gmm_clustering_analysis(data, ax):
    print("Analyzing data using Gaussian Mixture Model (GMM).")
    
    # Reshape data
    data = data.reshape(-1, 1)
    
    # Fit GMM
    gmm = GaussianMixture(n_components=3, random_state=42)
    gmm.fit(data)
    labels = gmm.predict(data)
    
    # Plot the results
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    
    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)
        
        xy = data[class_member_mask]
        ax.plot(xy[:, 0], np.zeros_like(xy[:, 0]) + 0.01, 'o', markerfacecolor=tuple(col),
                markeredgecolor='k', markersize=6, label=f'Cluster {k}')
    
    plot_distribution(ax, data, 'Gaussian Mixture Model (GMM)')
    
    # Set y-axis limits to match other plots
    ax.set_ylim(0, 0.5/3.25)
    ax.legend()
    
analysis_function_12 = gmm_clustering_analysis

# def gaussian_process_regression(data, ax):
#     print("Analyzing data using Gaussian Process Regression.")
    
#     # Scale the data
#     scaler = StandardScaler()
#     data_scaled = scaler.fit_transform(data.reshape(-1, 1))
    
#     kernel = C(1.0, (1e-4, 1e1)) * RBF(1, (1e-4, 1e1))
#     gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
    
#     x = np.linspace(data.min(), data.max(), 1000).reshape(-1, 1)
#     x_scaled = scaler.transform(x)
    
#     gpr.fit(data_scaled, data)
#     y_pred, sigma = gpr.predict(x_scaled, return_std=True)
    
#     plot_distribution(ax, data, 'Gaussian Process Regression')
#     ax.plot(x, y_pred, 'r-', label='GPR')
#     ax.fill_between(x.ravel(), y_pred - 1.96 * sigma, y_pred + 1.96 * sigma, alpha=0.2, color='r')
#     ax.legend()

def isolation_forest_analysis(data, ax):
    print("Analyzing data using Isolation Forest.")
    
    # Reshape data
    data = data.reshape(-1, 1)
    
    # Perform Isolation Forest analysis
    iso_forest = IsolationForest(contamination=0.1)
    labels = iso_forest.fit_predict(data)
    
    # Plot the results
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    
    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)
        
        xy = data[class_member_mask]
        label = 'Outliers' if k == -1 else 'Inliers'
        ax.plot(xy[:, 0], np.zeros_like(xy[:, 0]) + 0.01, 'o', markerfacecolor=tuple(col),
                markeredgecolor='k', markersize=6, label=label)
    
    plot_distribution(ax, data, 'Isolation Forest Clustering')
    ax.legend()

analysis_function_13 = isolation_forest_analysis

def bayesian_mixture_model(data, ax, n_components=3):
    print("Analyzing data using Bayesian Mixture Model.")
    bgmm = BayesianGaussianMixture(n_components=n_components)
    bgmm.fit(data.reshape(-1, 1))
    x = np.linspace(data.min(), data.max(), 1000).reshape(-1, 1)
    logprob = bgmm.score_samples(x)
    
    plot_distribution(ax, data, 'Bayesian Mixture Model')
    ax.plot(x, np.exp(logprob), 'r-', label='BMM')
    ax.legend()

analysis_function_14 = bayesian_mixture_model

def self_organizing_map(data, ax):
    print("Analyzing data using Self-Organizing Map.")
    som = MiniSom(1, 10, 1, sigma=0.3, learning_rate=0.5)
    som.random_weights_init(data.reshape(-1, 1))
    som.train_random(data.reshape(-1, 1), 100)
    
    plot_distribution(ax, data, 'Self-Organizing Map')
    weights = som.get_weights().reshape(-1)
    for weight in weights:
        ax.axvline(weight, color='r', linestyle='--')
        ax.text(weight, ax.get_ylim()[1], f'Weight: {weight:.2f}', 
                rotation=90, verticalalignment='top')

analysis_function_15 = self_organizing_map

analysis_functions = [
    analysis_function_1, analysis_function_2, analysis_function_3,
    analysis_function_4, analysis_function_5, analysis_function_6,
    analysis_function_7, analysis_function_8, analysis_function_9,
    analysis_function_10, analysis_function_11, analysis_function_12,
    analysis_function_13, analysis_function_14, analysis_function_15
]

def plot_all_functions(data, width_in=7, height_in=7):
    """Plot all 15 functions in a 4x4 grid with the top-left subplot showing the legend."""
    plt.close('all')  # Close previous plots
    fig, axes = plt.subplots(4, 4, figsize=(width_in, height_in))
    axes = axes.flatten()
    
    # Top-left subplot for the legend
    axes[0].axis('off')
    
    for i, (func, ax) in enumerate(zip(analysis_functions, axes[1:])):
        func(data, ax)
    
    # Create a dummy plot for the legend
    handles, labels = axes[1].get_legend_handles_labels()
    axes[0].legend(handles, labels, loc='center')
    
    plt.tight_layout()
    plt.show()

def plot_single_function(data, index, width_in=7, height_in=7):
    """Plot a single function based on the provided index."""
    plt.figure(figsize=(width_in, height_in))
    analysis_functions[index](data, plt.gca())
    plt.tight_layout()
    plt.show()

def analyze_multimodal_distribution(data):
    print("Analyze multimodal distribution using 15 different approaches.")
    
    # Enable interactive mode
    plt.ion()

    # Initial plot of all functions
    print("plotting all functions")
    plot_all_functions(data)
    print("all functions plotted")

    while True:
        choice = input("Enter a number between 1 and 9 or a-f to zoom in, z to zoom out, or q to exit: ").strip()
        if not choice:
            continue
        if choice == 'q':
            break
        elif choice == 'z':
            # Zoom-out to print all 15 plots at once (default view)
            plt.close('all')  # Close previous plots
            plot_all_functions(data)
        elif choice.isdigit() and 1 <= int(choice) <= 9:
            # Zoom-in to plot only the selected analysis function
            plt.close('all')  # Close previous plots
            plot_single_function(data, int(choice) - 1)
        elif choice in 'abcdef':
            # Zoom-in to plot only the selected analysis function
            plt.close('all')  # Close previous plots
            plot_single_function(data, ord(choice) - ord('a') + 9)
        else:
            print("Invalid input. Please enter a number between 1 and 9 or a-f.")

if __name__ == "__main__":
    # Generate sample multi-modal data
    np.random.seed(42)
    data = np.concatenate([
        np.random.normal(-5, 1, 1000),
        np.random.normal(0, 1.5, 1500),
        np.random.normal(5, 0.5, 500)
    ])

    analyze_multimodal_distribution(data)
    
    # a needs to be scaled vertically to match the other plots.