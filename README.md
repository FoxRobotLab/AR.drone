# AR.drone
Uses libardrone. Includes demo programs.  

### M and Rae's notes on the code:

#### AR Drone Code (AR.drone\libardrone)

__ar2video__ is just video encoding -- it's a wrapper for h264decoder

__arnetwork__ handles video input from camera and “nav_socket” input, whatever that is

__arvideo__ does all the video decoding - it’s a very large and very gross file (lots of hardcoding, repetition) so hopefully we won’t have to read it all?

__CSARDrone__ uses __MultiCamShift__(_mcs_) to orient drone to center target in vision. Tracks blue and pink. The original threaded version worked on the Windows machine we tried it on and presumably was originally working on a Linux box. (This remains in the Windows drone code folder.) Strange issues cropped up on Macs, the non-threaded version (in the main folder) should fix these.
    __CSARDrone__ decides how to move drone based on scores created in _patternReact_. There is tolerance built in that allows the color strip to not be in the exact center of the drone's view.  
    
__demo__ controls drone for demo (takeoff/land/move/speed). Control drone with keyboard. Accesses drone’s video. (Uses pygame for control.)

__FoxDemo__  controls drone for demo. Also uses keyboard (but with keyevents this time). Accesses drone’s camera for pictures. (uses tkinter to display images, which can be a problem)

__libardrone__ contains most of the tools for drone movement/manipulation. Three main sections: the first defines higher-level operations in terms of the low-level at (action type?) controls; the second defines said at controls (it looks like mostly this is just wrappers?); and the third claims to handle navdata packets (?).
It finishes with a testing method that allows manual control using keyboard commands. 

__MultiCamShift__ Handles the OpenCV work of finding the target in the image from the drone. Finds x, y position, relative area, and angle of marker. Uses __TargetScanner__ to find markers. Looking for a pattern of pink/blue/pink (or other specified colors) in a row.

__Tracker__ is used by __targetScanner__ is used by __MultiCamShift__ is used by __CSARDrone__.

So there’s quadrant division in __targetScanner__ and __tracker__ - __tracker__ functions like one would expect, it finds an object and tracks it with back projection. It contains an _update()_ method to update a camshift window. 
How __tracker__ gets the color: in __targetScanner__, calculate the back projection and then call _update()_ on the __tracker__, which sets the _self.backproj_ to the correct thing.
Searcher works by - it already has a back projection by this point, so searcher just calls update on a __tracker__, passing the known the back projection.



