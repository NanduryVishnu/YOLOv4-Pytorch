from .constants import *

# ImageInfo
class ImageInfo:
    """
    ----------
    Author: Damon Gwinn (gwinndr)
    ----------
    - Contains augmentation information about a given image
    - Used for tracking image positions for mapping back or cropping
    ----------
    """

    # __init__
    def __init__(self, image):
        # Original image
        self.org_image = image

        self.org_h = image.shape[CV2_H_DIM]
        self.org_w = image.shape[CV2_W_DIM]

        # Augmented image
        self.aug_image = image.copy()

        # Top left offset position
        self.aug_pleft = 0
        self.aug_ptop = 0

        # Width and height from the top left position
        self.aug_h = self.org_h
        self.aug_w = self.org_w

    # set_augmentation
    def set_augmentation(self, aug_image):
        """
        ----------
        Author: Damon Gwinn (gwinndr)
        ----------
        - Sets augmented image
        ----------
        """

        self.aug_image = aug_image

    # set_offset
    def set_offset(self, pleft, ptop):
        """
        ----------
        Author: Damon Gwinn (gwinndr)
        ----------
        - Sets the topleft position offset of the augmented image
        ----------
        """

        self.aug_pleft = pleft
        self.aug_ptop = ptop

        return

    # set_dimensions
    def set_dimensions(self, width, height):
        """
        ----------
        Author: Damon Gwinn (gwinndr)
        ----------
        - Sets the width and height of the augmented image
        ----------
        """

        self.aug_w = width
        self.aug_h = height
