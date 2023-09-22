# TinyLift

TinyLift is a demonstration elevator control system for access control integrations. It runs on a Raspberry Pi and uses a series of button inputs, LED status lights, and an LCD panel to display the current elevator cab status. 

TinyLift currently just simulates the logical control of an elevator. It's purpose is to test and demo access control integrations with systems that interrupt call button presses with relay control. The simulated elevator is a single cab that can travel up or down a virtual six-floor shaft. LED's (typically built into the call buttons themselves) operate similarly to a real elevator, turning on when buttons are pressed and turning off once the elevator "reaches" the given floor. 

An LCD panel tracks both the current direction the elevator is traveling and the current floor it is on, intended to mimic the readout of the inside of a real elevator cab.

The only required components are a Raspberry Pi 3B+ and the necessary buttons, hardware, and LCD readout. Other Raspberry Pi models with the same pinouts should work fine, though they are untested.

The materials used for the first build of the entire system are as follows:
1x Raspberry Pi 3B+
1x (optional) HCDC RPi GPIO Status LED & Terminal Block Breakout Board (https://www.amazon.com/gp/product/B08RDYDG6X)
8x DMWD 2PCS 19MM Momentary Push Button (https://www.amazon.com/gp/product/B09HTX7MHH)
8x 2N2222 Transistors
1x  TWI Serial LCD 2004 20x4 Display Module with I2C Interface Adapter (https://www.amazon.com/gp/product/B086VVT4NH)
1x Otdorpatio Project Box ABS Plastic Black Electrical Box (https://www.amazon.com/gp/product/B08N1DD5WJ/)
1x Multi-Channel Power Supply Module with 3.3V/5V/12V Output (https://www.amazon.com/gp/product/B08927SVJB/)
1x Breadboard (I used a solderable breadboard for the "final" implementation)
A considerable amount of 18 stranded and unstranded copper wire (multicolored is ideal to keep different inputs straight)

Electrical setup and wiring diagrams are included in the repo as well. 
