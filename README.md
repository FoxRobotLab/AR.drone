# AR.drone
Uses libardrone. Includes demo programs.  

M and Rae's notes on the code:

AR Drone Code (AR.drone\libardrone)

ar2video is just video encoding

arnetwork handles video input from camera and “nav_socket” input, whatever that is

arvideo does all the video decoding - it’s a very large and very gross file (lots of hardcoding, repetition) so hopefully we won’t have to read it all?

CSARDrone uses MultiCamShift(mcs) to orient drone to center target in vision. Tracks green and blue. 

demo controls drone for demo (takeoff/land/move/speed). Control drone with keyboard. Accesses drone’s video. (Uses pygame for control.)

FoxDemo  controls drone for demo. Also uses keyboard (but with keyevents this time). Accesses drone’s camera for pictures. (uses tkinter to display images, which can be a problem)

libardrone contains most of the tools for drone movement/manipulation. Three main sections: the first defines higher-level operations in terms of the low-level at (action type?) controls; the second defines said at controls (it looks like mostly this is just wrappers?); and the third claims to handle navdata packets (?).
It finishes with a testing method that allows manual control using keyboard commands. 

MultiCamShift we are wondering about what outer and inner color means here . This handles the OpenCV work of finding the target in the image from the drone. Finds x, y position, relative area, and angle of marker. Uses TargetScanner to find markers. 


Tracker is used by targetScanner is used by MultiCamShift is used by CSARDrone.

So there’s quadrant division in targetScanner and tracker - tracker functions like one would expect, it finds an object and tracks it with back projection. It contains an update() method to update a camshift window. 
How tracker gets the color: in targetScanner, calculate the back projection and then call update() on the tracker, which sets the self.backproj to the correct thing.
Searcher works by - it already has a back projection by this point, so searcher just calls update on a tracker, passing the known the back projection.



