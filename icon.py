import numpy as np
import matplotlib.pyplot as plt


def generate_infinity_symbol(num_points=1000):
    t = np.linspace(0, 2 * np.pi, num_points)
    x = np.sin(t)
    y = np.sin(t) * np.cos(t) / 1.4
    return np.column_stack((x, y))


def plot_infinity_symbol(
    num_points=1000, style="default", filename="infinity_symbol.svg"
):
    plt.style.use(style)
    plt.figure(figsize=(10, 10))
    points = generate_infinity_symbol(num_points)
    plt.plot(
        points[:, 0],
        points[:, 1],
        color="white" if style == "dark_background" else "black",
        linewidth=22,
    )
    axes = plt.gca()
    axes.set_aspect("equal")
    plt.axis("off")  # This will turn off the axis
    plt.tight_layout()
    plt.savefig(filename, format="svg", transparent=True)
    plt.clf()  # This clears the current plot, so the style of the next one will not be affected


# Light version
plot_infinity_symbol(style="default", filename="icon_light.svg")

# Dark version
plot_infinity_symbol(style="dark_background", filename="icon_dark.svg")
