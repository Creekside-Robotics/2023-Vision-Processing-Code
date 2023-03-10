# FRC 8775 Robotics - 2023 Vision Processing Code
This repository maintains our robot's vision and decision making code designed to power autonmous capability on our robot during the 2023 season.

## Goals
 - [x] Dynamic Object detection with Mobilenet2 
 - [x] Apriltag detection + Pose estimation
 - [ ] Full knowledge of surroundings by robot.
 - [ ] Exceutable tasks based on vision input
 - [ ] Advanced decision making capability
 - [ ] Adaptable to many settings in FRC


## Necessary Software
There is some software that you will need to work on the project.

- Install the python>=3.7 [here](https://www.python.org/). Be sure that the code is compatible with python==3.7.
- Install tensorflow using the following command `pip3 install tensorflow`
- Install opencv using the following command `pip3 install opencv-python`
- Install numpy using the following command `pip3 install numpy`
- Install pynetworktables using the following command `pip3 install pynetworktables`
- Install robotpy-cscore using the following command `python -m pip install --pre robotpy-cscore`
- Install scipy using the following command `pip3 install scipy`

## Documentation for WPILIB and other libraries
Documentation for of the important libraries used in this project.
 - [Tensorflow](https://www.tensorflow.org/guide) - Framework used to create models for vision processing and decision making
 - [Tensorflow Lite](https://www.tensorflow.org/lite/guide) - Scaled down version of tensorflow which we will be using on our hardware
 - [NetworkTables](https://robotpy.readthedocs.io/projects/pynetworktables/en/stable/api.html) - Library used to communicate with Roborio
 - [AprilTags](https://april.eecs.umich.edu/software/apriltag) - This is the main page for the apriltag robotics labratory. [Here](https://www.youtube.com/watch?v=TG9KAa2EGzQ&authuser=0) is a video that does a good job explaining what apriltags are and how to use them (1:40 - 2:40). Ignore information on photonvision, we will not be using that software.
 
 ## Branch Protection Rules
 `main` is the only protected branch. All changes that effect robot functionality must be merged to `main` via pull request and have been succesfully tested.

## Resolving Merge Conflicts

See something like this?

![image](https://user-images.githubusercontent.com/58612/178773622-c5c66379-4020-47f0-aa52-68d22b86744e.png)

DO NOT click that "Resolve Conflicts" button. Unfortunately GitHub makes resolving merge conflicts harder than it needs to
be, but don't worry! You can follow these steps and get your branch up to date
quickly.

For a full explanation you can watch [this video](https://www.youtube.com/watch?v=I0hUvy7SW6M). She shows an example and explains the whole process really well.

To do this you will need to run some commands in a terminal. VS Code has one you can access or you can use your system's terminal emulator (Windows Terminal on Windows 10+ or Terminal on OS X).

1. Ensure your local main is up to date.

```
git checkout main
git pull
```

2. Switch to your branch. Make sure to use your actual branch name in the command.

```
git checkout your-branch-name
```

3. Replay your commits on top of the current main. This is different from what GitHub instructs you to do, but this is the "correct" way to bring a branch up to date cleanly.

```
git rebase main
```

When you run this command it may ask you to manually resolve merge conflicts. It will show you what the change on main was alongside your change that conflicts with it. You'll need to manually edited those then `git add` each file once it looks good.

4. Update your remote branch with the changes.

```
git push --force-with-lease origin your-branch-name
```

That should do it! If you run into any issues with this please ask in our Discord server and someone will help you out.

