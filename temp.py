import os
import shutil
import datetime
import pyautogui as gui
import cv2
from skimage.metrics import structural_similarity
import imutils
import threading


def compare_images(image_one, image_two):

    """Compare 2 images.

    Args:
        image_one (str): File name of image one.
        image_two (str): File name of image two.

    Returns:
        dict: Compare results with indices
            "image_one"         : File name of image one.
            "image_two"         : File name of image two.
            "is_same_size"      : True if file resolution is same.
            "similarity_score"  : Similarity score. Range from 1 to -1 with 1 being same, -1 if nothing matching.
            "num_differences"   : Number of differences.
            "compared_image"    : File name of image highlighting differences.

    """

    # hold the final results
    compare_results = {}
    compare_results["image_one"] = image_one
    compare_results["image_two"] = image_two

    # read the images
    _image_one_cv = cv2.imread(image_one)
    _image_two_cv = cv2.imread(image_two)

    # check if the images are of same size
    is_same_size = False
    try:
        is_same_size = _image_one_cv.shape == _image_two_cv.shape
    except BaseException as be:
        print(f"Count not get the shape for {image_one} and {image_two}")
        print(be)

    compare_results["is_same_size"] = is_same_size

    if is_same_size:
        # get the difference for grey colors
        gray1 = cv2.cvtColor(_image_one_cv, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(_image_two_cv, cv2.COLOR_BGR2GRAY)

        # compute the Structural Similarity Index (SSIM)
        (score, difference) = structural_similarity(gray1, gray2, full=True)
        difference = (difference * 255).astype("uint8")
        compare_results["similarity_score"] = score

        # create an image with differences
        threshold = cv2.threshold(
            difference, 0, 128, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]
        cnts = cv2.findContours(
            threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnts = imutils.grab_contours(cnts)

        # loop over contours
        num_differences = 0
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            rect_area = w * h
            if rect_area > 10:
                num_differences += 1
                cv2.rectangle(_image_one_cv, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(_image_two_cv, (x, y), (x + w, y + h), (0, 0, 255), 2)

                _file_name = image_two.replace(".png", "_diff.png")
                cv2.imwrite(_file_name, _image_two_cv)
                compare_results["num_differences"] = num_differences
                compare_results["compared_image"] = _file_name

    return compare_results


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
        return _file_path
    except BaseException as e:
        print(f"unable to save the screenshot")
        print(e)


def save_screenshot_bursts(stop_event, path=".", interval=1, on_change=True):
    """Save screenshot bursts.

    Args:
        stop_event (thereading.Event()): Event to exit saving screenshots bursts.
        path (str, optional): Folder path to save the file. Defaults to ".".
        interval (int, optional): Interval between screenshots in seconds. Defaults to 2.
        on_change (bool, optional): Save screenshot only when screen changes. Defaults to True.
    """

    # save screenshot
    _previous_screen = save_screenshot(path=path)

    # save screenshot bursts untill specified exit interval
    while not stop_event.is_set():
        # save screenshot only on screen change
        if on_change:
            # save a new screenshot
            _current_screen = save_screenshot(path=path)

            # delete the saved screenshot if no change in screen
            compare_results = compare_images(_previous_screen, _current_screen)
            print(compare_results)
            if compare_results["similarity_score"] == 1:
                if os.path.exists(_current_screen):
                    os.remove(_current_screen)
            else:
                # move the difference image
                _file_name = compare_results["compared_image"].split("/")[-1]
                _root_folder = compare_results["compared_image"].replace(_file_name, "")
                _new_folder = "differences"
                _new_file_path = os.path.join(_root_folder, _new_folder)
                os.makedirs(_new_file_path, exist_ok=True)

                shutil.move(compare_results["compared_image"], _new_file_path)

                _previous_screen = _current_screen

        else:  # save the screenshot regardless of screen change
            save_screenshot(path=path)

        stop_event.wait(interval)


if __name__ == "__main__":
    # create an event to stop saving screenshots
    # used to signal termination to the threads
    stop_event = threading.Event()
    stop_event.wait(5)  # wait for sometime before starting

    # start saving screenshots in a thread
    thread = threading.Thread(
        target=save_screenshot_bursts,
        args=(stop_event, "screenshots/run1/ESG-TC-0000001", 1, True),
    )
    thread.start()

    # set the event event (Ctrl + C) to exit saving screenshots
    try:
        while True:
            continue
    except (KeyboardInterrupt, SystemExit):
        # stop saving screenshot bursts on Ctrl + C
        stop_event.set()
