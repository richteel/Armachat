# Armachat
Armachat Redesign from Peter Misenko's work at <a href="https://github.com/bobricius/Armachat-circuitpython">bobricius/Armachat-circuitpython</a>

This is a redesign of bobricius/Armachat-circuitpython repository to include:
-	All/most of the functionality that bobricius/Armachat-circuitpython intended
-	Allow the code to work on the Max, Compact and Watch versions of the hardware
-	Provide some confirmation messages
-	When not connected to a PC as a device on boot, allow saving of configuration information
-	Include detailed documentation for users and developers

## Updates/Notes
### 5 June 2022
I started working on the Armachat software early in 2022. I had started redesigning the software to make it more modular in April and decided to setup this separate repository in June as the work deviated considerably from the original bobricius/Armachat-circuitpython repository (code not functionality). My intent was to roll these changes into the bobricius/Armachat-circuitpython repository but the refactoring took it in a different direction with different challenges. Peter has also made several changes to the bobricius/Armachat-circuitpython repository that I have yet to evaluate and add to my code.
Currently, I recommend that folks use the bobricius/Armachat-circuitpython repository code as it is more responsive to keypresses than the code in this repository. The responsiveness issue is within the code that displays the lines of text to the screen. It is taking nearly a second to update the screen. In the time that the screen is refreshing, the user may push one or two more keys, which will be missed. This code will be refactored to improve responsiveness.

*To Do Items including bugs and challenges to resolve*
-	Speed up screen refresh to improve key press responsiveness
- Write User's Manual
- Write Developer's Guide
- Add setup on first boot and allow access through menu
- Add setup instructions in User's Manual
- Write Quick Start Guide
