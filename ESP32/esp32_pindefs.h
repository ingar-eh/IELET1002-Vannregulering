//Definerer CE og CSN-pinnene som RF-modulen bruker
#define CE 17
#define CSN 5

#define maxWaterLevel 390 //Max høyde på vann i cm i tanken
#define sequence 5 //Sensoren tar gjennomsnittet av x verdier 
#define discardValue 3 //Hvis to etterfølgende sensor verdier varierer med discardValue (cm) blir de forkastet

//dette er for å fjerne useriøse sensormålinger som kan oppstå
#define sendInterval 5000 //Intervallet i millisekund vi skal sende data
#define triggerPin 14
#define echoPin 26
#define greenLed 12
#define redLed 27
#define blueLed 13
#define rightButton 35
#define leftButton 34
#define enableMOSFET 25