import numpy
import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle


def plot_light_curve(times, fluxes):
    "Plot light curve of system"

    # Plot light curve
    plt.scatter(times, fluxes, s=8, color='black', label='LPSEB35 Data')
    plt.axvline(75, color="green", linestyle="-.", label='Egress start')
    plt.axvline(150, color="blue", linestyle="-.", label='Egress end')
    plt.xlabel('Minutes after observation', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel('LPSEB35 flux / Comparison flux ratio', fontsize=16)
    plt.grid(linestyle=":", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('figures/light_curve.pdf', dpi=300)
    plt.clf()


def determine_period(times, fluxes):
    "Determine period of system with LombScargle"

    # Convert times to hours
    time_hour = times / 60

    # Perform LombScargle to find frequency
    frequency, power = LombScargle(time_hour, fluxes).autopower()

    # Pick the best frequency
    best_freq = frequency[numpy.argmax(power)]

    # The actual period is twice the period of the periodiogram
    period = 2/best_freq

    # Plot periodogram
    plt.plot(frequency, power)
    plt.axvline(x=best_freq, label="Best frequency", color='green', linestyle="-.")
    plt.xlabel("Frequency (1 / h)", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel("Power", fontsize=16)
    plt.xlim(0, 6)
    plt.tick_params(axis='both', which='major')
    plt.grid(linestyle=":", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/periodogram.pdf")
    plt.clf()

    return period


def plot_phase_folded(times, fluxes, period):
    """Plot a phase-folded light curve with eclipse depth"""

    # Convert time to days for consistency
    time_days = times / (60 * 24)
    period_days = period / 24

    # Phase-fold the data
    phase = (time_days % period_days) / period_days

    # Optionally sort by phase for plotting
    mag = -2.5 * numpy.log10(fluxes)

    # Sort for smooth plotting
    sorted_idx = numpy.argsort(phase)
    phase_sorted = phase[sorted_idx]
    mag_sorted = mag[sorted_idx]

    # Define in-eclipse and out-of-eclipse regions by phase
    in_eclipse = (phase > 0.2) & (phase < 0.3)
    out_of_eclipse = (phase > 0.49) & (phase < 0.52)

    # Compute median magnitudes
    mag_eclipse = numpy.median(mag[in_eclipse])
    mag_out = numpy.median(mag[out_of_eclipse])

    # Calculate eclipse depth
    depth_mag = mag_eclipse - mag_out
    print(f"Eclipse Depth: {depth_mag:.3f} mag")
    
    # Plot phase-folded light curve
    plt.scatter(phase_sorted, mag_sorted, s=7, color='black', label="Data")
    plt.axhline(mag_out, color='green', linestyle='--', label="Out-of-Eclipse")
    plt.axhline(mag_eclipse, color='blue', linestyle='--', label="In-Eclipse")
    plt.xlabel("Phase", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel("Relative Magnitude", fontsize=16)
    plt.gca().invert_yaxis()
    plt.grid(linestyle=":", alpha=0.5)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('figures/phase_plot.pdf')
    plt.clf()


if __name__ == "__main__":

    # Load the datas
    times = numpy.load("times.npy") # minutes
    fluxes = numpy.load("fluxes.npy")    

    # Plot all plots
    plot_light_curve(times, fluxes)

    period = determine_period(times, fluxes)
    print(f"Period: {period:.3f} h")

    plot_phase_folded(times, fluxes, period)