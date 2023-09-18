# tcview-thermal-camera-python

# Description
Code for interacting with the tcview TC001 thermal camera using OpenCV and Python.

# Features
- Interpolates the image from the camera and increases resolution for better viewing and recording.
- Has 10 different colormaps that can be applied to the image.
- Records maximum, minimum, average temperature of the sceen.
- Track the temperature of any number of pixels on the screen with time.
- Saves recorded data as .csv files and also plots and saves the data as pdf files automatically.
- Has video recording and snapshot taking abilities.

# Commands
These keypresses need to be done when the video display window is focused.
1. `'['` - Start recording the data (Start experiment). NOTE: This starts a fresh timer and is not recommended to do this more than once every time the application is run.
`']'` - Stop the experiment.
2. `'a'` - Increase blur radius, `'z'` - Decrease blur radius.
3. `','` - Turn on the display of floating max and min temperatures (Turnt on by default), `'.'` - Turn off the floating max and min temperatures.
4. `'s'` - Decrease threshold, `'x'` - Increase threshold.
5. `'d'` - Increase scale of the image, `'c'` - Decrease scale.
6. `'i'` - Enable fullscreen, `'w'` - Disable fullscreen.
7. `'f'` - Increase contrast, `'v'` - Decrease contrast.
8. `'h'` - Press to show/hide HUD.
9. `'m'` - Cycle through the available colormaps.
10. `'r'` - Start recording, `'t'` - Finish recording.
11. `'p'` - Take a screenshot.
12. `'q'` - QUIT the application.

# Custom pixel tracking
In the code, you can change the `pixels` variable to include any number of pixel coordinates in the format `[line,column]`. Two pixels are already added as template and may be removed.
The data from the pixels in saved in numbered .csv files in the directory mentioned in `fi` variable (Default is './'). The numbers are assigned in the same order as the pixels are included in the `pixels` variable, in increasing order (i.e. The first coordinates will be assigned the number 0, the second 1, and so on).
The plots from the data recorded from the pixels is also stored in the same directory as .pdf files using the same numbering scheme. The x-axis is time from the beginning of the experiment in ms, and the y-axis is the temperature in Kelvin.

# Other configurations
Comments in the code describe the functionality of the other crucial variables. They may be changed to suit the requirement of the user.

# Installation / Running
The code requires the following dependencies to run -
- opencv-python
- numpy
- matplotlib

The code can be cloned from the repo using the `git clone` command. Run `tc001v*.py` file using python.


# NOTE
The `dev` variable is set to define the video ID of the device that openCV will read - this is the ID of the thermal camera in thi case. In computers that do not have any other video input devices, this is generally `0`. However, in other systems it may be any other number.

# Changelog
- 18.09.2023 : Improved the README.md file and added instructions for use. Bugfixed cursor and temperature drawing on the screen of the video display. Added comments and improved readability of the code. Added option to remove the floating display of max and min temperatures.

# Credits
- Built on top of Les Wright's repo - https://github.com/leswright1977/PyThermalCamera/
- Reverse engineering of the camera thanks to LeoDJ on EEVBlog Forums - https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
- Additional help from LeoDJ's repo for the Infiray camera - https://github.com/LeoDJ/P2Pro-Viewer/tree/main

# To-Do
- [ ] Add ability to record the temperature profile of the entire scene.
- [ ] Add the ability to click and select pixels for tracking instead of specifying coordinates in code.
- [ ] Improve data representation.