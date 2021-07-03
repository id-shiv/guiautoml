import os
import datetime
import pyautogui as gui
import cv2


def compare_images(image1, image2):
    """Compare 2 images.

    Args:
        image1 (str): Image to compare.
        image2 (str): Image to be compared against.

    Returns:
        int: Difference of image pixels.
            -2      : Error processing shape
            -1      : Images are of different shape
            0       : Images are same
            positive: Images are diffent. Number indicates magnitude of difference.
    """

    # read the images
    _image1_cv = cv2.imread(image1)
    _image2_cv = cv2.imread(image2)

    # check if the images are of same size
    is_same_size = False
    try:
        is_same_size = _image1_cv.shape == _image2_cv.shape
    except BaseException as be:
        print(f"Count not get the shape for {image1} and {image2}")
        print(be)
        return -2

    if is_same_size:
        # calculate the difference
        _image_diff = cv2.subtract(_image1_cv, _image2_cv)

        # uncomment this if you want to view the difference image
        # cv2.imshow("diff", _image_diff)
        # cv2.waitKey(0)

        # get the difference for blue, green & red colors
        b, g, r = cv2.split(_image_diff)

        # add the difference for blue, green & red colors
        _difference_cv = cv2.countNonZero(b) + cv2.countNonZero(g) + cv2.countNonZero(r)
        # cv2.imshow("diff", _difference_cv)
        # cv2.waitKey(0)

        # images are same if the sum of all differences is 0
        if _difference_cv == 0:
            print(f"images {image1} and {image2} are same")
            return 0
        else:
            print(
                f"images {image1} and {image2} are different with a difference of {_difference_cv}"
            )
            return _difference_cv
    else:
        print(f"images {image1} and {image2} are of different shape")
        return -1


def save_screenshot(path=".", file_name="current_time_stamp", file_extension="png"):
    """Save screenshot to a file.

    Args:
        path (str, optional): Folder path to save the file. Defaults to ".".
        file_name (str, optional): File name. Defaults to "current_time_stamp".
        file_extension (str, optional): File extension. Defaults to ".png".

    Returns:
        str: File path of the saved the screenshot.
    """

    # create folder for the screenshot to be saved
    try:
        os.makedirs(path, exist_ok=False)
    except FileExistsError as e:
        pass
    except BaseException as e:
        print(f"unable to create folder {path}")
        print(e)

    # generate filepath for the screenshot to be saved
    try:
        # generate the filename as current timestamp if not input
        if file_name == "current_time_stamp":
            _datenow = str(datetime.datetime.now())
            file_name = _datenow.replace(" ", "-").replace(":", "-").replace(".", "-")

        _file_path = os.path.join(path, file_name + "." + file_extension)
    except BaseException as e:
        print(f"unable to generate the file path")
        print(e)

    # save the screenshot
    try:
        gui.screenshot(_file_path)
        print(f"screenshot saved as {_file_path}")
        return _file_path
    except:
        print(f"unable to save the screenshot")
        print(e)


def save_screenshot_bursts(path=".", interval=2, on_change=True, exit_interval=10):
    """Save screenshot bursts.

    Args:
        path (str, optional): Folder path to save the file. Defaults to ".".
        interval (int, optional): Interval between screenshots in seconds. Defaults to 2.
        on_change (bool, optional): Save screenshot only when screen changes. Defaults to True.
        exit_interval (int, optional): Interval to exit saving screenshots in seconds. Defaults to 10.
    """

    duration = 0  # duration to be incremented till exit interval

    # save screenshot
    _previous_screen = save_screenshot(path=path)

    # save screenshot bursts untill specified exit interval
    while duration < exit_interval:
        gui.sleep(interval)

        # save screenshot only on screen change
        if on_change:
            # save a new screenshot
            _current_screen = save_screenshot(path=path)

            # delete the saved screenshot if no change in screen
            if compare_images(_previous_screen, _current_screen) == 0:
                if os.path.exists(_current_screen):
                    os.remove(_current_screen)
                    print(f"screenshot {_current_screen} deleted")
            else:
                _previous_screen = _current_screen

        else:  # save the screenshot regardless of screen change
            save_screenshot(path=path)

        duration += interval


if __name__ == "__main__":
    # save_screenshot_bursts(
    #     path="screenshots", interval=5, on_change=True, exit_interval=60
    # )
    compare_images(
        "screenshots/2021-07-03-22-30-20-745487.png",
        "screenshots/2021-07-03-22-30-26-132129.png",
    )
