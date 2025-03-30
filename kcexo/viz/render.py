# -*- coding: UTF-8 -*-
import io
import matplotlib as plt


def render_to_png(fig: plt.figure.Figure, clear_fig: bool = True) -> bytes:
    """Renders the `matplotlib` figure in to a PNG-encoded `bytes` array and optionally clear/close the figure.
    
    .. note::
        After running this method the plot is no longer available if the `clear_fig` was set to True.

    Args:
        fig (plt.figure.Figure): The figure to render
        clear_fig (bool, optional): Should the figure be cleared and closed? Default it True.

    Returns:
        bytes: PNG-encoded image
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    image_data: bytes = buf.getvalue()  # Get the image data as bytes
    buf.close()
    if clear_fig:
        fig.clear()
        plt.pyplot.close(fig)
    return image_data
