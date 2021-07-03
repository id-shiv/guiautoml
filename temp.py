import pyautogui as gui
import datetime
import os


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
            if 1 == 1:
                if os.path.exists(_current_screen):
                    os.remove(_current_screen)
                    print(f"screenshot {_current_screen} deleted")
                _previous_screen = _current_screen
        else:  # save the screenshot regardless of screen change
            save_screenshot(path=path)

        duration += interval


save_screenshot_bursts(path="screenshots", on_change=False)
