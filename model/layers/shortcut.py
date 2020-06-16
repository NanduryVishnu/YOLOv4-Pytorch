import torch
import torch.nn as nn

from utilities.constants import SHCT_ACTIV

# ShortcutLayer
class ShortcutLayer(nn.Module):
    """
    ----------
    Author: Damon Gwinn (gwinndr)
    ----------
    - A darknet Shortcut layer
    ----------
    """

    # __init__
    def __init__(self, from_layer, activation=SHCT_ACTIV):
        super(ShortcutLayer, self).__init__()

        self.has_learnable_params = False
        self.requires_layer_outputs = True

        self.from_layer = from_layer
        self.activation = activation

        # TODO: Add more activations
        if((self.activation != "linear") and (self.activation is not None)):
            print("ShortcutLayer: Warning: Ignoring unrecognized activation:", self.activation)

    # get_required_layers
    def get_required_layers(self):
        """
        ----------
        Author: Damon Gwinn (gwinndr)
        ----------
        - Gets the layer index for shortcutting (residual connection), can be negative
        ----------
        """

        return (self.from_layer,)

    # forward
    def forward(self, x, layer_outputs):
        """
        ----------
        Author: Damon Gwinn (gwinndr)
        ----------
        - Runs the shortcut (residual connection)
        - Must give output from the layer specified by from_layer
        ----------
        """
        output_from_layer = layer_outputs[0]

        res = x + output_from_layer

        # TODO: Add more activations
        return res

    # to_string
    def to_string(self):
        """
        ----------
        Author: Damon Gwinn (gwinndr)
        ----------
        - Converts this layer into a human-readable string
        ----------
        """

        return \
            "SHCT: layer: %d  activ: %s" % \
            (self.from_layer, self.activation)
